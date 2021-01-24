from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import ugettext_lazy  as _

# Create your models here.
class MyUser(AbstractUser):
    USERNAME_FIELD = 'email'
    email = models.EmailField(_('email address'), unique=True) # changes email to unique and blank to false
    # REQUIRED_FIELDS = [] # removes email from REQUIRED_FIELDS
    REQUIRED_FIELDS = ['first_name']

    def __str__(self): 
        return "{}".format(self.email)