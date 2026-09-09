from django import forms


class PhoneLoginForm(forms.Form):
    phone = forms.CharField(
        widget=forms.HiddenInput(attrs={'id': 'id_phone'}),
    )
    phone_country = forms.CharField(label='Страна', required=False)
