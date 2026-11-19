from urllib.parse import quote
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods
from .forms import RegistrationForm, AccommodationForm
from .models import Registration, Accommodation

COMMITTEE_WHATSAPP = "919880485128"


def _wa(reg):
    lines = [f"Registration for Utsav 2026 (20 Dec, Satsang Vihar Bengaluru)", f"ID: {reg.reg_id}",
             f"Name: {reg.name}", f"Phone: {reg.phone}", f"City: {reg.city}",
             f"Adults: {reg.adults}, Children: {reg.children}", f"Satsangee: {reg.satsangee}"]
    if reg.interests:
        lines.append("Take part in: " + ", ".join(reg.interests))
    return f"https://wa.me/{COMMITTEE_WHATSAPP}?text=" + quote("\n".join(lines))


@require_http_methods(["GET", "POST"])
def home(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            d = form.cleaned_data
            reg = Registration.objects.create(
                name=d["name"].strip(), phone=d["phone"], email=d["email"], city=d["city"].strip(),
                adults=d["adults"], children=d["children"] or "0", satsangee=d["satsangee"],
                centre=d["centre"].strip(), interests=d["interests"], message=d["message"].strip(),
                consent=True)
            request.session["last_reg"] = reg.pk  # only this browser can see its own thank-you card
            return redirect("thanks")
        return render(request, "home.html", {"form": form}, status=400)
    return render(request, "home.html", {"form": RegistrationForm()})


def thanks(request):
    pk = request.session.get("last_reg")
    reg = Registration.objects.filter(pk=pk).first() if pk else None
    if not reg:
        return redirect("home")
    return render(request, "home.html", {"reg": reg, "wa_url": _wa(reg)})


def _acc_wa(a):
    lines = ["Accommodation request for Utsav 2026 (20 Dec, Satsang Vihar Bengaluru)", f"ID: {a.acc_id}",
             f"Name: {a.name}"] + ([f"Family code: {a.family_code}"] if a.family_code else []) + [
             f"WhatsApp: {a.whatsapp}", f"City: {a.city}", f"Satsang Vihar: {a.satsang_vihar}",
             f"Type: {a.acc_type}, Devotees: {a.devotees}",
             f"Arrival: {a.eta_date} {a.eta_time}".strip(), f"Departure: {a.etd_date} {a.etd_time}".strip(),
             f"Transport: {a.transport}"]
    return f"https://wa.me/{COMMITTEE_WHATSAPP}?text=" + quote("\n".join(lines))


@require_http_methods(["GET", "POST"])
def accommodation(request):
    if request.method == "POST":
        form = AccommodationForm(request.POST)
        if form.is_valid():
            d = form.cleaned_data
            fmt = lambda t: t.strftime("%I:%M %p").lstrip("0") if t else ""
            a = Accommodation.objects.create(
                name=d["name"].strip(), family_code=d["family_code"].strip(), whatsapp=d["whatsapp"],
                city=d["city"].strip(), satsang_vihar=d["satsang_vihar"].strip(), acc_type=d["acc_type"],
                devotees=int(d["devotees"]), eta_date=d["eta_date"], eta_time=fmt(d["eta_time"]),
                etd_date=d["etd_date"], etd_time=fmt(d["etd_time"]), transport=d["transport"])
            request.session["last_acc"] = a.pk
            return redirect("acc_thanks")
        return render(request, "accommodation.html", {"form": form}, status=400)
    return render(request, "accommodation.html", {"form": AccommodationForm()})


def acc_thanks(request):
    pk = request.session.get("last_acc")
    a = Accommodation.objects.filter(pk=pk).first() if pk else None
    if not a:
        return redirect("accommodation")
    return render(request, "accommodation.html", {"acc": a, "wa_url": _acc_wa(a)})
