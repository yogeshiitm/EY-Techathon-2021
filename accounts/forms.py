from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.models import User
from django.forms import ValidationError
from django.contrib import messages


class CustomRegisterForm(UserCreationForm):
    email = forms.EmailField(label = "Email", max_length=75, required=True)
    fullname = forms.CharField(label = "Full name", max_length=75, required=True)

    class Meta:
        model = User
        fields = ("fullname", "email")

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).exists():
            raise forms.ValidationError(u'Email already exists!')
        return email


    def save(self, commit=True):
        user = super(CustomRegisterForm, self).save(commit=False)
        list = self.cleaned_data["fullname"].split()
        print(list)
        firstname = list[0]
        lastname = ' '.join(list[1:])

        user.first_name = firstname.capitalize()
        user.last_name = lastname.capitalize()
        user.email = self.cleaned_data["email"]

        if commit and not User.objects.filter(email = user.email).exists():
            user.save()
        return user