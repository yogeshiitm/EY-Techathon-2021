from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.models import User
from django.forms import ValidationError
from django.contrib import messages
from .models import *


from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.forms import ValidationError
from django.contrib import messages
# from django.contrib.auth.models import User
# replace the above with
from django.contrib.auth import get_user_model
User = get_user_model()

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


class MedicalForm(forms.ModelForm):
    class Meta:
        model = MedicalModel
        fields = ('adhaar','mobile','category','state','district','age','gender','covid','smoker','hbp_hyt','respiratory','chd','diabetes','cancer_non','hmt','reduced_kidney','kidney_dialysis','liver_disease','other_neuro','organ_transplant')
        #fields = ('covid',)
