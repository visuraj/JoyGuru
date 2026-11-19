"""One-click Excel export for Utsav registrations and accommodation requests."""
import io
from datetime import datetime

from django.http import HttpResponse
from django.utils import timezone

XLSX_MIME = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

# (column heading, function(obj) -> value, column width)
REGISTRATION_COLUMNS = [
    ("Reg ID", lambda r: r.reg_id, 14),
    ("Name", lambda r: r.name, 26),
    ("Mobile", lambda r: r.phone, 14),
    ("Email", lambda r: r.email, 28),
    ("City / area", lambda r: r.city, 20),
    ("Adults", lambda r: r.adults, 9),
    ("Children", lambda r: r.children, 9),
    ("Satsangee?", lambda r: r.satsangee, 14),
    ("Satsang centre", lambda r: r.centre, 22),
    ("Take part in", lambda r: ", ".join(r.interests or []), 30),
    ("Message", lambda r: r.message, 40),
    ("Registered at", lambda r: r.created_at, 20),
]

ACCOMMODATION_COLUMNS = [
    ("Request ID", lambda a: a.acc_id, 15),
    ("Devotee name", lambda a: a.name, 26),
    ("Family code", lambda a: a.family_code, 14),
    ("WhatsApp", lambda a: a.whatsapp, 14),
    ("City", lambda a: a.city, 20),
    ("Satsang Vihar", lambda a: a.satsang_vihar, 22),
    ("Accommodation type", lambda a: a.acc_type, 18),
    ("Total devotees", lambda a: a.devotees, 10),
    ("ETA date", lambda a: a.eta_date, 13),
    ("ETA time", lambda a: a.eta_time, 10),
    ("ETD date", lambda a: a.etd_date, 13),
    ("ETD time", lambda a: a.etd_time, 10),
    ("Mode of transport", lambda a: a.transport, 16),
    ("Submitted at", lambda a: a.created_at, 20),
]


def _write_sheet(wb, title, columns, rows, fmts):
    ws = wb.add_worksheet(title)
    for c, (head, _, width) in enumerate(columns):
        ws.write_string(0, c, head, fmts["head"])
        ws.set_column(c, c, width)
    ws.freeze_panes(1, 0)
    n = 0
    for n, obj in enumerate(rows, start=1):
        for c, (_, getter, _w) in enumerate(columns):
            v = getter(obj)
            if isinstance(v, datetime):
                if timezone.is_aware(v):
                    v = timezone.localtime(v).replace(tzinfo=None)  # Excel has no tz support
                ws.write_datetime(n, c, v, fmts["dt"])
            elif isinstance(v, (int, float)) and not isinstance(v, bool):
                ws.write_number(n, c, v)
            else:
                # write_string never treats text as a formula (blocks "=cmd|..." injection)
                # and keeps phone numbers as text so leading zeros are not lost.
                ws.write_string(n, c, "" if v is None else str(v))
    if n:
        ws.autofilter(0, 0, n, len(columns) - 1)
    return n


def build_workbook(sheets):
    """sheets: list of (sheet title, columns, iterable of objects) -> xlsx bytes."""
    import xlsxwriter

    buf = io.BytesIO()
    wb = xlsxwriter.Workbook(buf, {"in_memory": True, "constant_memory": True})
    fmts = {
        "head": wb.add_format({"bold": True, "bg_color": "#F4B183", "border": 1}),
        "dt": wb.add_format({"num_format": "dd-mmm-yyyy hh:mm"}),
    }
    for title, columns, rows in sheets:
        _write_sheet(wb, title, columns, rows, fmts)
    wb.close()
    return buf.getvalue()


def xlsx_response(filename_prefix, sheets):
    stamp = timezone.localtime().strftime("%Y%m%d_%H%M")
    resp = HttpResponse(build_workbook(sheets), content_type=XLSX_MIME)
    resp["Content-Disposition"] = f'attachment; filename="{filename_prefix}_{stamp}.xlsx"'
    return resp


# ---------------------------------------------------------------------------
# Smart multi-sheet report: Summary + Registrations + Accommodation + Matched
# ---------------------------------------------------------------------------
import re
from collections import Counter

INTERESTS = ["Health camp", "Career counselling", "Legal counselling", "Painting competition",
             "Dancing performance", "Sishuloka"]
ARRIVAL_DATES = ["19 December 2026", "20 December 2026"]
DEPART_DATES = ["20 December 2026", "21 December 2026"]


def _num(s):
    """'6 or more' -> 6, '2' -> 2 (minimum head-count; blanks -> 0)."""
    m = re.match(r"\d+", str(s or ""))
    return int(m.group()) if m else 0


def _phone(s):
    return re.sub(r"\D", "", str(s or ""))[-10:]


MATCH_COLUMNS = [
    ("Reg ID", lambda p: p[0].reg_id, 14), ("Name (registration)", lambda p: p[0].name, 24),
    ("Mobile", lambda p: p[0].phone, 14), ("City", lambda p: p[0].city, 18),
    ("Adults", lambda p: p[0].adults, 9), ("Children", lambda p: p[0].children, 9),
    ("Request ID", lambda p: p[1].acc_id, 15), ("Devotee name (accommodation)", lambda p: p[1].name, 24),
    ("Family code", lambda p: p[1].family_code, 13), ("Satsang Vihar", lambda p: p[1].satsang_vihar, 20),
    ("Type", lambda p: p[1].acc_type, 12), ("Devotees", lambda p: p[1].devotees, 10),
    ("ETA date", lambda p: p[1].eta_date, 18), ("ETA time", lambda p: p[1].eta_time, 10),
    ("ETD date", lambda p: p[1].etd_date, 18), ("ETD time", lambda p: p[1].etd_time, 10),
    ("Transport", lambda p: p[1].transport, 11),
]


def build_full_workbook(regs, accs):
    """regs / accs: iterables of model objects -> xlsx bytes with 4 sheets."""
    import xlsxwriter

    regs, accs = list(regs), list(accs)
    nr, na = len(regs), len(accs)
    buf = io.BytesIO()
    wb = xlsxwriter.Workbook(buf, {"in_memory": True})
    fmts = {
        "head": wb.add_format({"bold": True, "bg_color": "#F4B183", "border": 1}),
        "dt": wb.add_format({"num_format": "dd-mmm-yyyy hh:mm"}),
    }
    title = wb.add_format({"bold": True, "font_size": 16})
    sect = wb.add_format({"bold": True, "bg_color": "#E07B2A", "font_color": "#FFFFFF"})
    lab = wb.add_format({"border": 1})
    val = wb.add_format({"border": 1, "bold": True, "align": "right"})

    # Summary is added first so it is the first tab; filled after the data sheets exist.
    sm = wb.add_worksheet("Summary")
    _write_sheet(wb, "Registrations", REGISTRATION_COLUMNS, regs, fmts)
    _write_sheet(wb, "Accommodation", ACCOMMODATION_COLUMNS, accs, fmts)

    # --- Matched sheet: people who registered AND asked for accommodation (same mobile) ---
    by_phone = {}
    for a in accs:
        by_phone.setdefault(_phone(a.whatsapp), []).append(a)
    pairs = [(r, a) for r in regs for a in by_phone.get(_phone(r.phone), [])]
    _write_sheet(wb, "Registered + Accommodation", MATCH_COLUMNS, pairs, fmts)

    # --- Summary (live formulas, so it stays right if the sheets are edited) ---
    R, A = f"Registrations!${{c}}$2:${{c}}${nr + 1}", f"Accommodation!${{c}}$2:${{c}}${na + 1}"
    r_rng = lambda c: R.format(c=c)
    a_rng = lambda c: A.format(c=c)
    sm.set_column(0, 0, 38); sm.set_column(1, 2, 16)
    sm.write(0, 0, "Utsav 2026 · Satsang Vihar Bengaluru — Summary", title)
    sm.write(1, 0, "Generated " + timezone.localtime().strftime("%d-%b-%Y %H:%M"))
    row = [3]

    def section(name, *heads):
        sm.write(row[0], 0, name, sect)
        for i, h in enumerate(heads, 1):
            sm.write(row[0], i, h, sect)
        row[0] += 1

    def line(label, formula, value, formula2=None, value2=None):
        sm.write(row[0], 0, label, lab)
        sm.write_formula(row[0], 1, formula, val, value)
        if formula2:
            sm.write_formula(row[0], 2, formula2, val, value2)
        row[0] += 1

    section("REGISTRATIONS", "Count")
    line("Total registrations", f"=COUNTA({r_rng('A')})", nr)
    line("Adults (6 or more counted as 6)", f"=SUMPRODUCT(--LEFT({r_rng('F')},1))" if nr else "=0",
         sum(_num(r.adults) for r in regs))
    line("Children (4 or more counted as 4)", f"=SUMPRODUCT(--LEFT({r_rng('G')},1))" if nr else "=0",
         sum(_num(r.children) for r in regs))
    for label in ("Yes, Satsangee", "No, first visit"):
        line(f"  {label}", f'=COUNTIF({r_rng("H")},"{label}")', sum(r.satsangee == label for r in regs))
    row[0] += 1
    section("WANT TO TAKE PART IN", "Count")
    for it in INTERESTS:
        line(f"  {it}", f'=COUNTIF({r_rng("J")},"*{it}*")', sum(it in (r.interests or []) for r in regs))
    row[0] += 1
    section("ACCOMMODATION REQUESTS", "Requests", "Devotees")
    line("Total", f"=COUNTA({a_rng('A')})", na, f"=SUM({a_rng('H')})", sum(a.devotees for a in accs))
    for t in ("Family", "Individual", "Group"):
        line(f"  {t}", f'=COUNTIF({a_rng("G")},"{t}")', sum(a.acc_type == t for a in accs),
             f'=SUMIF({a_rng("G")},"{t}",{a_rng("H")})', sum(a.devotees for a in accs if a.acc_type == t))
    row[0] += 1
    section("ARRIVALS (ETA)", "Requests", "Devotees")
    for d in ARRIVAL_DATES:
        line(f"  {d}", f'=COUNTIF({a_rng("I")},"{d}")', sum(a.eta_date == d for a in accs),
             f'=SUMIF({a_rng("I")},"{d}",{a_rng("H")})', sum(a.devotees for a in accs if a.eta_date == d))
    row[0] += 1
    section("DEPARTURES (ETD)", "Requests", "Devotees")
    for d in DEPART_DATES:
        line(f"  {d}", f'=COUNTIF({a_rng("K")},"{d}")', sum(a.etd_date == d for a in accs),
             f'=SUMIF({a_rng("K")},"{d}",{a_rng("H")})', sum(a.devotees for a in accs if a.etd_date == d))
    row[0] += 1
    section("MODE OF TRANSPORT", "Requests", "Devotees")
    for t in ("Train", "Car", "Flight"):
        line(f"  {t}", f'=COUNTIF({a_rng("M")},"{t}")', sum(a.transport == t for a in accs),
             f'=SUMIF({a_rng("M")},"{t}",{a_rng("H")})', sum(a.devotees for a in accs if a.transport == t))
    row[0] += 1
    section("REGISTERED + ACCOMMODATION", "Count")
    line("Matched by mobile number", f"=COUNTA('Registered + Accommodation'!$A$2:$A${len(pairs) + 1})", len(pairs))
    row[0] += 1
    section("TOP 10 CITIES (registrations)", "Count")
    for city, n in Counter(r.city.strip().title() for r in regs).most_common(10):
        sm.write(row[0], 0, "  " + city, lab); sm.write_number(row[0], 1, n, val); row[0] += 1
    wb.close()
    return buf.getvalue()


def full_xlsx_response(regs, accs):
    stamp = timezone.localtime().strftime("%Y%m%d_%H%M")
    resp = HttpResponse(build_full_workbook(regs, accs), content_type=XLSX_MIME)
    resp["Content-Disposition"] = f'attachment; filename="utsav2026_all_data_{stamp}.xlsx"'
    return resp
