import csv
from django.contrib import admin
from django.http import HttpResponse
from django.urls import path
from .models import Registration, Accommodation
from .exports import xlsx_response, REGISTRATION_COLUMNS, ACCOMMODATION_COLUMNS

admin.site.site_header = "Utsav 2026 · Satsang Vihar Bengaluru"
admin.site.site_title = "Utsav admin"
admin.site.index_title = "Registrations"


@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = ("reg_id", "name", "phone", "city", "adults", "children", "satsangee", "created_at")
    list_filter = ("satsangee", "adults", "city", "created_at")
    search_fields = ("reg_id", "name", "phone", "email", "city", "centre")
    date_hierarchy = "created_at"
    actions = ["export_csv", "export_selected_excel"]
    list_per_page = 50

    def get_urls(self):
        return [path("export-excel/", self.admin_site.admin_view(self.export_excel_all),
                     name="registrations_registration_export_excel")] + super().get_urls()

    def export_excel_all(self, request):
        """One click: every registration (oldest first) as an .xlsx file."""
        if not self.has_view_permission(request):
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied
        qs = Registration.objects.order_by("created_at")
        return xlsx_response("utsav2026_registrations",
                             [("Registrations", REGISTRATION_COLUMNS, qs.iterator(chunk_size=2000))])

    @admin.action(description="Download selected registrations as Excel")
    def export_selected_excel(self, request, queryset):
        return xlsx_response("utsav2026_registrations_selected",
                             [("Registrations", REGISTRATION_COLUMNS, queryset.order_by("created_at").iterator(chunk_size=2000))])

    def get_readonly_fields(self, request, obj=None):
        return [f.name for f in self.model._meta.fields]   # view-only: records can't be altered

    def has_add_permission(self, request):
        return False

    @admin.action(description="Download selected registrations as CSV")
    def export_csv(self, request, queryset):
        resp = HttpResponse(content_type="text/csv")
        resp["Content-Disposition"] = 'attachment; filename="utsav2026_registrations.csv"'
        w = csv.writer(resp)
        w.writerow(["Reg ID", "Name", "Mobile", "Email", "City", "Adults", "Children", "Satsangee",
                    "Centre", "Take part in", "Message", "Registered at"])
        for r in queryset:
            w.writerow([r.reg_id, r.name, r.phone, r.email, r.city, r.adults, r.children, r.satsangee,
                        r.centre, ", ".join(r.interests), r.message, r.created_at.isoformat()])
        return resp


@admin.register(Accommodation)
class AccommodationAdmin(admin.ModelAdmin):
    list_display = ("acc_id", "name", "family_code", "whatsapp", "city", "satsang_vihar", "acc_type",
                    "devotees", "eta_date", "etd_date", "transport", "created_at")
    list_filter = ("acc_type", "eta_date", "etd_date", "transport", "satsang_vihar")
    search_fields = ("acc_id", "name", "family_code", "whatsapp", "city", "satsang_vihar")
    date_hierarchy = "created_at"
    actions = ["export_csv", "export_selected_excel"]
    list_per_page = 50

    def get_urls(self):
        return [path("export-excel/", self.admin_site.admin_view(self.export_excel_all),
                     name="registrations_accommodation_export_excel")] + super().get_urls()

    def export_excel_all(self, request):
        """One click: every accommodation request (oldest first) as an .xlsx file."""
        if not self.has_view_permission(request):
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied
        qs = Accommodation.objects.order_by("created_at")
        return xlsx_response("utsav2026_accommodation",
                             [("Accommodation", ACCOMMODATION_COLUMNS, qs.iterator(chunk_size=2000))])

    @admin.action(description="Download selected accommodation requests as Excel")
    def export_selected_excel(self, request, queryset):
        return xlsx_response("utsav2026_accommodation_selected",
                             [("Accommodation", ACCOMMODATION_COLUMNS, queryset.order_by("created_at").iterator(chunk_size=2000))])

    def get_readonly_fields(self, request, obj=None):
        return [f.name for f in self.model._meta.fields]

    def has_add_permission(self, request):
        return False

    @admin.action(description="Download selected accommodation requests as CSV")
    def export_csv(self, request, queryset):
        resp = HttpResponse(content_type="text/csv")
        resp["Content-Disposition"] = 'attachment; filename="utsav2026_accommodation.csv"'
        w = csv.writer(resp)
        w.writerow(["Request ID", "Name", "Family code", "WhatsApp", "City", "Satsang Vihar", "Type", "Devotees",
                    "ETA date", "ETA time", "ETD date", "ETD time", "Transport", "Submitted at"])
        for r in queryset:
            w.writerow([r.acc_id, r.name, r.family_code, r.whatsapp, r.city, r.satsang_vihar, r.acc_type,
                        r.devotees, r.eta_date, r.eta_time, r.etd_date, r.etd_time, r.transport, r.created_at.isoformat()])
        return resp
