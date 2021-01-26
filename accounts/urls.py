from django.urls import path
from . import views

urlpatterns = [
    
    path("login", views.login, name='login'),
    path("admin_login", views.admin_login, name='admin_login'),
    path("signup", views.signup, name='signup'),
    path("logout", views.logout_user, name='logout'),
    path("dashboard", views.dashboard, name='dashboard'),
    path("vaccineform", views.vaccineform, name='vaccineform'),
    path("healthadmin", views.healthadmin, name='healthadmin')
]