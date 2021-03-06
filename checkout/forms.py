from django import forms
from .models import Order

""" Code adapted from Boutique Ado walkthrough project """


class OrderForm(forms.ModelForm):
    """Checkout form"""
    class Meta:
        model = Order
        fields = ('full_name', 'email',
                  'phone_number', 'street_address',
                  'post_code', 'town_or_city',
                  'country',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        placeholders = {
            'full_name': 'Full Name',
            'email': 'Email',
            'phone_number': 'Phone Number',
            'street_address': 'Street Address',
            'post_code': 'Postal Code',
            'town_or_city': 'Town or City',
        }

        self.fields['full_name'].widget.attrs['autofocus'] = True
        for field in self.fields:
            if field != 'country':
                if self.fields[field].required:
                    placeholder = f'{placeholders[field]} *'
                else:
                    placeholder = placeholders[field]
                self.fields[field].widget.attrs['placeholder'] = placeholder
                self.fields[field].widget.attrs['class'] = (
                    'stripe_style_input input-border')
            else:
                self.fields[field].widget.attrs['class'] = (
                    'stripe_style_input input-border my-select')
            self.fields[field].label = False
