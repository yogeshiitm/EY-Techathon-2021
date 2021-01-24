from django.db import models
from django.contrib.auth.models import User
from vaccine_delivery.models import StateModel

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

STATES = []
for state in StateModel.objects.all():
    STATES.append((f"{state.state}",state.state)) 
STATES = tuple(STATES)

CATEGORY = (
    ("Health Worker/Frontline Worker", 1.1),
    ("Senior Citizens", 1.2),
    ("People with Comorbidities", 1.3),
    ("Others",1.4)
)

# Create your models here.
class MedicalModel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    adhaar = models.CharField(max_length=16, blank=False)
    mobile = models.CharField(max_length=10,blank=False)
    pincode = models.CharField(max_length=6, blank=False)
    category = models.CharField(max_length = 100, blank=False)
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

    def __str__(self):
        return f'{self.user.username}-{self.state}'
    
    def funct():
        pass
    
    # class Meta:
    #     ordering = ['category']


