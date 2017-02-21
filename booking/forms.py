from django import forms
import floppyforms.__future__ as forms

from .models import Bid, Booking, Consumer, Contractor, Transaction


class BidForm_Agent(forms.ModelForm):

    class Meta:
        model = Bid
        fields = ['booking','contractor','base_cost','premium_adjustment',
        'status']

    def clean(self):
        booking = self.cleaned_data.get('booking')


class BidForm(forms.ModelForm):

    class Meta:
        model = Bid
        fields = ['base_cost','premium_adjustment',
        'status']

    def clean(self):
        booking = self.cleaned_data.get('booking')


class BookingForm(forms.ModelForm):

    class Meta:
        model = Booking
        fields = ['consumer','address_1','address_2','access_instructions',
        'suburb','phone_number_2','post_code','preferred_schedule',
        'category','subtypes', 'quoted_price','cost_adjustment','base_cost',
        'priority_level','completed','status','comment_private',
        'comment_public','link']

    def clean(self):
        address_1 = self.cleaned_data.get('address_1')




class ConsumerForm(forms.ModelForm):

    class Meta:
        model = Consumer
        fields = ['name','phone_number','email_address']

    def clean(self):
        name = self.cleaned_data.get('name')
        phone_number = self.cleaned_data.get('phone_number')
        email_address = self.cleaned_data.get('email_address')


class ContractorForm(forms.ModelForm):

    class Meta:
        model = Contractor
        fields = ['name','categories','phone_number','active']

    def clean(self):
        name = self.cleaned_data.get('name')
        phone_number = self.cleaned_data.get('phone_number')


class TransactionForm(forms.ModelForm):

    class Meta:
        model = Transaction
        fields = ['transaction_type','amount','source_agent','contractor',
        'source_type','target_bid','status','comment']

    def clean(self):
        amount = self.cleaned_data.get('amount')
