from django import forms

class SearchForm(forms.Form):
    state = forms.CharField(max_length =80)