from django.contrib.admin.views.decorators import staff_member_required
from django.core.exceptions import PermissionDenied

from .exports import full_xlsx_response
from .models import Registration, Accommodation


@staff_member_required
def export_all_excel(request):
    """One workbook: Summary + Registrations + Accommodation + Registered/Accommodation matches."""
    u = request.user
    if not (u.has_perm("registrations.view_registration") and u.has_perm("registrations.view_accommodation")):
        raise PermissionDenied
    return full_xlsx_response(Registration.objects.order_by("created_at"),
                              Accommodation.objects.order_by("created_at"))
