import json

import requests
from django.forms import forms, ModelForm

from .models import BankDetails

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
