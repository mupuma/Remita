

import json

import requests
from django.forms import forms, ModelForm

from .models import BankDetails, Users
from django import forms as djforms
class BankDetailsForm(ModelForm):
    def __int__(self, *args, **kwargs):
        super(BankDetailsForm, *args, **kwargs)
        self.fields['account_no'].label = "Account Number"
        #self.fields['vendor_id'].label = "Vendor ID"
        self.fields['account_name'].label = "Account Name"
        self.fields['vendor_mobile_number'].label = "Beneficiary Mobile Number"
        self.fields['vendor_email'].label = "Beneficiary Email"
        self.fields['bank_code'].label = "Bank Code"


    class Meta:
        model = BankDetails
        fields = ['account_no', 'account_name', 'vendor_email', 'vendor_mobile_number', 'bank_name',
                   'bank_code']
        error_messages = {
            'account_no': {
                'required': 'Please enter the Account Number.',
                'null': 'The Account Number entered is invalid.',
            },
            # 'vendor_id': {
            #     'required': 'Please enter the Vendor ID.',
            #     'null': 'No Vendor available with Vendor ID entered.',
            # },
            'account_name': {
                'required': 'Please enter the account name.',
                'null': 'The Account Name cannot be null.',
            },
            'vendor_mobile_number': {
                'required': 'Please enter the Vendor Mobile Number.',
                'null': 'The Vendor Mobile Number cannot be null.',
            },
            'vendor_email': {
                'required': 'Please enter the Vendor Email.',
                'null': 'The Vendor Email cannot be null.',
            },
            'bank_code': {
                'required': 'Please enter the Sort Code.',
                'null': 'The Sort Code entered is invalid .',
            },
        }

class RegistrationForm(djforms.Form):
    username = djforms.CharField(max_length=150)
    email = djforms.EmailField(required=True)
    role = djforms.ChoiceField(choices=(('001', '001'), ('002', '002')))
    password1 = djforms.CharField(widget=djforms.PasswordInput)
    password2 = djforms.CharField(widget=djforms.PasswordInput)

    def clean_username(self):
        username = self.cleaned_data['username']
        if Users.objects.filter(username=username).exists():
            raise djforms.ValidationError('This username is already taken.')
        return username

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get('password1')
        p2 = cleaned.get('password2')
        if p1 and p2 and p1 != p2:
            raise djforms.ValidationError('Passwords do not match.')
        return cleaned

    def save(self) -> Users:
        user = Users.objects.create_user(
            username=self.cleaned_data['username'],
            password=self.cleaned_data['password1'],
            role=self.cleaned_data['role'],
        )
        user.email = self.cleaned_data['email']
        # Ensure inactive until approval
        user.is_active = False
        user.save(update_fields=['email', 'is_active'])
        return user
