import re
from django import forms

ADULTS = [("", "Select"), ("1", "1"), ("2", "2"), ("3", "3"), ("4", "4"), ("5", "5"), ("6 or more", "6 or more")]
KIDS = [("0", "0"), ("1", "1"), ("2", "2"), ("3", "3"), ("4 or more", "4 or more")]
SAT = [("Yes, Satsangee", "Yes, I am a Satsangee"), ("No, first visit", "No, this is my first visit")]
PARTS = [("Health camp", "Health camp"), ("Career counselling", "Career counselling"),
         ("Legal counselling", "Legal counselling"), ("Painting competition", "Painting competition (child)"),
         ("Dancing performance", "Dancing performance"),
         ("Sishuloka", "Sishuloka (performance by the children of Bengaluru Satsang)"),
         ("Volunteer seva", "Volunteer for seva")]


class RegistrationForm(forms.Form):
    name = forms.CharField(min_length=2, max_length=120, error_messages={"required": "Enter your full name."})
    phone = forms.CharField(max_length=20, error_messages={"required": "Enter your mobile number."},
                            widget=forms.TextInput(attrs={"type": "tel", "inputmode": "numeric", "placeholder": "10-digit number"}))
    email = forms.EmailField(required=False, error_messages={"invalid": "Enter a valid email address or leave it empty."})
    city = forms.CharField(max_length=100, error_messages={"required": "Enter your city or area."})
    adults = forms.ChoiceField(choices=ADULTS, error_messages={"required": "Select how many adults are coming."})
    children = forms.ChoiceField(choices=KIDS, required=False)
    satsangee = forms.ChoiceField(choices=SAT, widget=forms.RadioSelect, error_messages={"required": "Choose one option."})
    centre = forms.CharField(max_length=120, required=False)
    interests = forms.MultipleChoiceField(choices=PARTS, required=False, widget=forms.CheckboxSelectMultiple)
    message = forms.CharField(max_length=1000, required=False, widget=forms.Textarea(attrs={"rows": 3}))
    consent = forms.BooleanField(error_messages={"required": "Please tick this box to continue."})
    website = forms.CharField(required=False)  # honeypot: bots fill it, people never see it

    def clean_phone(self):
        p = re.sub(r"[\s-]", "", self.cleaned_data["phone"])
        p = re.sub(r"^(\+91|91|0)(?=\d{10}$)", "", p)
        if not re.fullmatch(r"[6-9]\d{9}", p):
            raise forms.ValidationError("Enter a valid 10-digit mobile number.")
        return p

    def clean_website(self):
        if self.cleaned_data.get("website"):
            raise forms.ValidationError("Invalid.")
        return ""


ACC_TYPE = [("Family", "Family"), ("Individual", "Individual"), ("Group", "Group")]
COUNT = [("", "Select")] + [(str(i), str(i)) for i in range(1, 7)]
ETA_DATES = [("", "Select"), ("19 December 2026", "19 December 2026"), ("20 December 2026", "20 December 2026")]
ETD_DATES = [("", "Select"), ("20 December 2026", "20 December 2026"), ("21 December 2026", "21 December 2026")]
TRANSPORT = [("Train", "Train"), ("Car", "Car"), ("Flight", "Flight")]


class AccommodationForm(forms.Form):
    name = forms.CharField(min_length=2, max_length=120, error_messages={"required": "Enter the devotee name."})
    family_code = forms.CharField(max_length=40, error_messages={"required": "Enter your family code."})
    whatsapp = forms.CharField(max_length=20, error_messages={"required": "Enter the WhatsApp number."},
                               widget=forms.TextInput(attrs={"type": "tel", "inputmode": "numeric", "placeholder": "10-digit number"}))
    city = forms.CharField(max_length=100, error_messages={"required": "Enter your city."})
    satsang_vihar = forms.CharField(max_length=120, error_messages={"required": "Enter your Satsang Vihar."})
    acc_type = forms.ChoiceField(choices=ACC_TYPE, widget=forms.RadioSelect, error_messages={"required": "Choose one option."})
    devotees = forms.ChoiceField(choices=COUNT, error_messages={"required": "Select the total number of devotees."})
    eta_date = forms.ChoiceField(choices=ETA_DATES, error_messages={"required": "Select the arrival date."})
    eta_time = forms.TimeField(required=False, widget=forms.TimeInput(attrs={"type": "time"}), error_messages={"invalid": "Enter a valid time."})
    etd_date = forms.ChoiceField(choices=ETD_DATES, error_messages={"required": "Select the departure date."})
    etd_time = forms.TimeField(required=False, widget=forms.TimeInput(attrs={"type": "time"}), error_messages={"invalid": "Enter a valid time."})
    transport = forms.ChoiceField(choices=TRANSPORT, widget=forms.RadioSelect, error_messages={"required": "Choose one option."})
    website = forms.CharField(required=False)  # honeypot

    def clean_whatsapp(self):
        p = re.sub(r"[\s-]", "", self.cleaned_data["whatsapp"])
        p = re.sub(r"^(\+91|91|0)(?=\d{10}$)", "", p)
        if not re.fullmatch(r"[6-9]\d{9}", p):
            raise forms.ValidationError("Enter a valid 10-digit WhatsApp number.")
        return p

    def clean_website(self):
        if self.cleaned_data.get("website"):
            raise forms.ValidationError("Invalid.")
        return ""
