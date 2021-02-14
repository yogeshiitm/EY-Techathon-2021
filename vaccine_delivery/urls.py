from django.urls import path,include
from .views import *

urlpatterns = [
    path('', Index, name="index"),
    # path('state_map', StateMapView, name='state_map'),
    path('district_level', DistrictHomeView, name='states'),
    path('district_level/<state>', DistrictView, name='district_level'),
    path('batch/<batch>', BatchView, name='batch'),
    path('about', AboutView, name= 'about'),
    path('team', TeamView, name= 'team'),
    path('sitemap', SitemapView, name= 'sitemap'),
    path("donation", DonationView, name='donation'),
]