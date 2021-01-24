from django.db import models
from django.contrib.auth.models import User
from vaccine_delivery.models import StateModel
from django.contrib.auth.models import AbstractUser
from django.utils.translation import ugettext_lazy  as _
from django.contrib.auth.base_user import BaseUserManager
from vaccine_delivery.models import *


class CustomUserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifiers
    for authentication instead of usernames.
    """
    def create_user(self, email, password, **extra_fields):
        """
        Create and save a User with the given email and password.
        """
        if not email:
            raise ValueError(_('The Email must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        return self.create_user(email, password, **extra_fields)


# Create your models here.
class CustomUser(AbstractUser):
    #https://tech.serhatteker.com/post/2020-01/email-as-username-django/
    username = None
    email = models.EmailField(_('email address'), unique=True) # changes email to unique and blank to false

    USERNAME_FIELD = 'email'
    # REQUIRED_FIELDS = [] # removes email from REQUIRED_FIELDS
    REQUIRED_FIELDS = ['first_name'] # don't add email to REQUIRED_FIELDS

    objects = CustomUserManager()

    def __str__(self): 
        return "{}".format(self.email)


GENDER = (
    ("M", "Male"),
    ("F","Female"),
    ('O',"Other")
)

ASTHAMA = (
    ("With no recent OCS use",1.2),
    ("With recent OCS use",1.1)
)

HTM = (
    ("Diagnosed <1 year ago", 1.1),
    ("Diagnosed ≥5 years ago", 1.2),
    ("Diagnosed 1–4.9 years ago", 1.3)
)

REDUCED_KIDNEY = (
    ("eFGR 30-60", 1.2),
    ("eFGR <30", 1.1),
)


CATEGORY = (
    ("Health Worker/Frontline Worker", 1.1),
    ("Senior Citizens", 1.2),
    ("People with Comorbidities", 1.3),
    ("Others",1.4)
)

# Create your models here.
class MedicalModel(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    adhaar = models.CharField(max_length=16, blank=False)
    mobile = models.CharField(max_length=10,blank=False)
    pincode = models.CharField(max_length=6, blank=False)
    occupation = models.CharField(max_length = 100, blank=False)
    state = models.CharField(max_length=100, blank=False)
    district = models.CharField(max_length=100, blank=False)
    age = models.CharField(max_length=100,blank=False)
    gender = models.CharField(max_length=100, blank=False)

    covid = models.IntegerField()
    smoker = models.IntegerField()
    hbp_hyt = models.IntegerField()
    respiratory = models.IntegerField()
    chd = models.IntegerField()
    diabetes = models.IntegerField()
    cancer_non = models.IntegerField()
    hmt = models.IntegerField()
    reduced_kidney = models.IntegerField()
    kidney_dialysis = models.IntegerField()
    liver_disease = models.IntegerField()
    strk_dmtia = models.IntegerField()
    other_neuro = models.IntegerField()
    organ_transplant = models.IntegerField()
    no_illness = models.IntegerField(null =True)
    category = models.IntegerField(null=True)
    illness_score = models.FloatField(null=True)

    def __str__(self):
        return f'{self.user.first_name}-{self.state}'
    
    def get_category(self):
        no_illness = self.smoker + self.hbp_hyt +self.respiratory +self.chd +self.diabetes +self.cancer_non +self.hmt +self.reduced_kidney +self.kidney_dialysis +self.liver_disease +self.strk_dmtia +self.other_neuro + self.organ_transplant

        if self.occupation == 'Health/Frontline Workers':
            self.category = 1
            self.no_illness = no_illness
            self.save()
        
        elif self.occupation == 'Others' and int(self.age) >= 60:
            self.category = 2
            self.no_illness = no_illness
            self.save()
        
        elif self.occupation == 'Others' and int(self.age) <60 and no_illness > 0:
            self.category = 3
            self.no_illness = no_illness
            self.save()
        else:
            self.category = 4
            self.no_illness = no_illness
            self.save()
    
    def set_eligibility(self):
        score = self.no_illness*1 + self.covid*1 + self.smoker*0.11 + self.hbp_hyt*0.14 + self.respiratory*0.215 + self.chd*0.33 + self.diabetes*0.26 + self.cancer_non*0.28 + self.hmt*0.46 + self.reduced_kidney*0.9 + self.kidney_dialysis*0.8 + self.liver_disease*0.18 + self.strk_dmtia*0.62 + self.other_neuro*0.39 + self.organ_transplant*0.34
        self.illness_score = score
        self.save()
        
    class Meta:
        ordering = ['category']


