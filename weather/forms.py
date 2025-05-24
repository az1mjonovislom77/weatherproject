from django import forms

class CityForm(forms.Form):
    city = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'placeholder': 'Name of city',
            'class': 'form-control',
            'autocomplete': 'on'
        })
    )
