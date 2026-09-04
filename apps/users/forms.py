from django import forms
from django.utils.translation import gettext_lazy as _
from phonenumber_field.formfields import PhoneNumberField


class PhoneLoginForm(forms.Form):
    phone = PhoneNumberField(
        label=_('Номер телефона'),
        widget=forms.HiddenInput(attrs={'id': 'id_phone'}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['phone'].widget.input_type = 'hidden'
