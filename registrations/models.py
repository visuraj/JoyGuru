import secrets
from django.db import models


def new_reg_id():
    return "UT26-" + secrets.token_hex(3).upper()


class Registration(models.Model):
    reg_id = models.CharField("Registration ID", max_length=16, unique=True, default=new_reg_id, editable=False)
    name = models.CharField(max_length=120)
    phone = models.CharField("Mobile", max_length=10, db_index=True)
    email = models.EmailField(blank=True)
    city = models.CharField("City / area", max_length=100)
    adults = models.CharField(max_length=12)
    children = models.CharField(max_length=12, default="0")
    satsangee = models.CharField("Satsangee?", max_length=30)
    centre = models.CharField("Satsang centre", max_length=120, blank=True)
    interests = models.JSONField(default=list, blank=True)
    message = models.TextField(blank=True)
    consent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.reg_id} · {self.name}"


def new_acc_id():
    return "ACC26-" + secrets.token_hex(3).upper()


class Accommodation(models.Model):
    acc_id = models.CharField("Request ID", max_length=16, unique=True, default=new_acc_id, editable=False)
    name = models.CharField("Devotee name", max_length=120)
    family_code = models.CharField(max_length=40, blank=True)
    whatsapp = models.CharField("WhatsApp number", max_length=10, db_index=True)
    city = models.CharField(max_length=100)
    satsang_vihar = models.CharField("Satsang Vihar", max_length=120)
    acc_type = models.CharField("Accommodation type", max_length=20)
    devotees = models.PositiveSmallIntegerField("Total devotees")
    eta_date = models.CharField("ETA date", max_length=20)
    eta_time = models.CharField("ETA time", max_length=12, blank=True)
    etd_date = models.CharField("ETD date", max_length=20)
    etd_time = models.CharField("ETD time", max_length=12, blank=True)
    transport = models.CharField("Mode of transport", max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "accommodation requests"

    def __str__(self):
        return f"{self.acc_id} · {self.name}"
