from django.urls import path
from .  import views

urlpatterns = [
    path("", views.home, name ="home"),
    path("loginPage", views.loginPage, name ="loginPage"),
    path("login", views.login, name ="login"),
    path('mainMenu', views.mainMenu, name='mainMenu'),
    path('mfa_setup', views.mfa_setup, name='mfa_setup'),
    path('verify_mfa/', views.verify_mfa, name='verify_mfa'),
]