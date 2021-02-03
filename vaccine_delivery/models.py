from django.db import models


# Create your models here.
class StateModel(models.Model):
    state = models.CharField(max_length=100)
    active = models.IntegerField()
    population_2020 = models.IntegerField()
    accessibility = models.IntegerField()
    children = models.IntegerField()
    senior_citizen = models.IntegerField()
    all_health_workers_percent = models.FloatField()
    death_rate = models.FloatField()
    ratio_vacant_beds = models.FloatField()
    batch_no= models.IntegerField()
    percentage_vaccine_delivery = models.FloatField()

    def __str__(self):
        return f'{self.state}-{self.active}' 
    
    class Meta:
       ordering = ['batch_no', 'percentage_vaccine_delivery']



class DistrictModel(models.Model):
    state = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    active = models.IntegerField()
    population_2020 = models.IntegerField()
    batch_no = models.IntegerField()

    def __str__(self):
        return f'{self.state}-{self.active}'
