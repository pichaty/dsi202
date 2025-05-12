# work/dsi202/pawpal/myapp/forms.py
from django import forms
from django.contrib.auth.models import User

class UserProfileEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name']
        help_texts = {
            'username': None,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = "ชื่อผู้ใช้ (Username)"
        self.fields['first_name'].label = "ชื่อจริง (First Name)"
        self.fields['last_name'].label = "นามสกุล (Last Name)"

        for field_name in self.fields:
            self.fields[field_name].widget.attrs.update({'class': 'form-control profile-form-input'}) # เพิ่ม class สำหรับ styling