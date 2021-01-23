from django.urls import path
from . import views

urlpatterns = [
    path("login", views.login, name='login'),
    path("signup", views.signup, name='signup'),
    path("logout", views.logout_user, name='logout'),
    path("dashboard", views.dashboard, name='dashboard'),
    path("profile", views.profile, name='profile')

]