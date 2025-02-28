from django.urls import path
from .  import views
from django.views.generic import TemplateView

urlpatterns = [
    path("", views.home, name ="home"),
    path("loginPage", views.loginPage, name ="loginPage"),
    path("login", views.login, name ="login"),

    path("loginReact", views.LoginView.as_view(), name ="loginReact"),
    path("registerReact", views.RegisterView.as_view(), name ="registerReact"),
    path("mfa_setupReact", views.MFASetupView.as_view(), name ="mfa_setupReact"),
    path('verify_mfaReact', views.VerifyMFAView.as_view(), name='verify_mfaReact'),
    path('update_mfa_enabledReact', views.UpdateMFAView.as_view(), name='update_mfa_enabledReact'),
    
    path('mainMenu', views.mainMenu, name='mainMenu'),
    path('mfa_setup', views.mfa_setup, name='mfa_setup'),
    path('verify_mfa/', views.verify_mfa, name='verify_mfa'),
    path('update_mfa_enabled/', views.update_mfa_enabled, name='update_mfa_enabled'),

    path('get_mfa_status/', views.get_mfa_status, name='get_mfa_status'),

    path('react', TemplateView.as_view(template_name='index.html')),
]