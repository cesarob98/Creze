import io
from django.shortcuts import render, redirect
from django.db import connection
from django.contrib import messages
from django.contrib.auth import login
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import LoginAttempt, User, customUser
from django.views.decorators.http import require_http_methods
from django.utils.timezone import timedelta
import pytz
import qrcode
from datetime import datetime
from django.db.models import F
import pyotp
import base64

tz = pytz.timezone('America/Mexico_City')


# Create your views here.
def home(request):
    return render(request, "Prelogin/home.html")

def loginPage(request):
    if 'logged_in' not in request.session or request.session.get('logged_in') is False:
        return render(request, 'Prelogin/login.html')
    else:
        messages.warning(request, 'Ya iniciaste sesión')
        return redirect('mainMenu')

def login_required_session(view_func):
    def wrapper(request, *args, **kwargs):
        if 'logged_in' not in request.session or request.session.get('logged_in') is False:
            messages.warning(request, 'Se requiere iniciar sesión para ver este contenido')
            return HttpResponseRedirect(reverse('loginPage'))
        return view_func(request, *args, **kwargs)
    return wrapper

@login_required_session
def mfa_setup(request):
    if 'logged_in' in request.session and 'otp_token' in request.session and request.session.get('otp_token') is True:
        messages.warning(request, 'Ya iniciaste sesión')
        return redirect('mainMenu')
    user_id = request.session['user_id']
    user, created = customUser.objects.get_or_create(user_id=user_id)
    if not user.mfa_secret:
        user.mfa_secret = pyotp.random_base32()
        user.save()
    otp_uri = pyotp.totp.TOTP(user.mfa_secret).provisioning_uri(
        name=user.email,
        issuer_name="CESAR"
    )

    qr = qrcode.make(otp_uri)
    buffer = io.BytesIO()
    qr.save(buffer, format="PNG")
    
    
    buffer.seek(0)  
    qr_code = base64.b64encode(buffer.getvalue()).decode("utf-8")

    qr_code_data_uri = f"data:image/png;base64,{qr_code}"
    now = datetime.now(tz)
    user.login_validity = now
    user.save()
    return render(request, 'Postlogin/mfa_setup.html', {"qrcode": qr_code_data_uri})

@login_required_session
def mainMenu(request):
    
    if 'otp_token' not in request.session or request.session.get('otp_token') is False:
        messages.warning(request, 'Se requiere completar el token para continuar')
        return HttpResponseRedirect(reverse('mfa_setup'))
    return render(request, 'Postlogin/MainMenu.html')



def verify_mfa(request):
    if request.method == 'POST':
        otp = request.POST.get('otp_code')
        user_id = request.session['user_id']
        if not user_id:
            messages.error(request, 'Invalid user id. Please try again.')
            return redirect('mfa_setup')
        
        user = customUser.objects.get(user_id=user_id)
        totp = pyotp.TOTP(user.mfa_secret)
        
        now = datetime.now(tz) 
        print(f"now = {now}, valid until =>{user.login_validity} =>{user.login_is_valid()}")
        if not user.login_is_valid():
            messages.error(request, f'Login has expired! Log again')
            request.session.flush()
            return redirect('loginPage')
        if totp.verify(otp):
            request.session['otp_token'] = True
            messages.success(request, 'Login exitoso!')
            return redirect('mainMenu')
        else:
            messages.error(request, f'Invalid OTP code. Please try again.')
            return redirect('mfa_setup')
       
    return redirect('mfa_setup')

def login(request):
    if request.GET.get('logout') == 'True':
        request.session.flush()
        messages.success(request, 'Sesión Terminada con éxito')
        return redirect('home')

    elif request.method == 'POST':
        user_name = request.POST['user_name']
        password = request.POST['password']

        # Check login attempts
        attempt, created = LoginAttempt.objects.get_or_create(username=user_name)
        attempt.attempts += 1
        attempt.save()
        print('previously on: ', attempt, created)
        if attempt.is_blocked():
            print('Blocked until: ', attempt.blocked_until)
            messages.error(request, 'Demasiados intentos fallidos. Intenta de nuevo más tarde.')
            return redirect('loginPage')

        with connection.cursor() as cursor:
            cursor.callproc('main.login', [user_name, password])
            result = cursor.fetchone()

            if result:
                user_id = result[0]
                user_name = result[1]
                attempt.attempts = 0
                attempt.blocked_until = None
                attempt.save()
                user = User.objects.get(user_id = user_id)
                user.user_name=user_name
                request.session['user_id'] = user.user_id
                request.session['logged_in'] = True
                request.session['otp_token'] = False
                messages.success(request, 'Login exitoso!')
                return redirect('mfa_setup')
            else:

                now = datetime.now(tz) 
                if attempt.attempts >= 5:
                    attempt.blocked_until = now + timedelta(minutes=5)
                attempt.save()
                messages.error(request, 'Login fallido!')
                return redirect('loginPage')

    else:
        return redirect('home')
    
