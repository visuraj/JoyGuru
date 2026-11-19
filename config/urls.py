from django.contrib import admin
from django.urls import path
from django.conf import settings
from registrations import views
from registrations.admin_views import export_all_excel

urlpatterns = [
    path(settings.ADMIN_URL + "export-all-excel/", export_all_excel, name="export_all_excel"),
    path(settings.ADMIN_URL, admin.site.urls),
    path("", views.home, name="home"),
    path("thanks/", views.thanks, name="thanks"),
    path("accommodation/", views.accommodation, name="accommodation"),
    path("accommodation/thanks/", views.acc_thanks, name="acc_thanks"),
]
