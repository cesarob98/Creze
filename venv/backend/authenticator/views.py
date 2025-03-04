import io
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import render, redirect
from django.db import DatabaseError, connection
from django.contrib import messages
from django.contrib.auth import login
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import LoginAttempt, User, customUser
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils.timezone import timedelta
import pytz, json
import qrcode
from datetime import datetime
from django.db.models import F
import pyotp
from django.core.cache import cache
import base64
from django_ratelimit.decorators import ratelimit

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
    user_id = request.session['user_id']
    user, created = User.objects.get_or_create(user_id=user_id)
    print(f"welcome user: {user}")
    return render(request, 'Postlogin/mainMenu.html', {"user_name": user.user_name, "mfa_enabled": user.mfa_enabled})


@require_http_methods(['POST'])
def update_mfa_enabled(request):
    try:
        if request.method == 'POST':
            data = json.loads(request.body)
            mfa_enabled = data.get('mfa_enabled')
            uid = request.session.get('user_id')
            if uid is None:
                return JsonResponse({'error': 'User ID not found in session'}, status=400)
            user = User.objects.filter(user_id=uid).first()
            if not user:
                return JsonResponse({'error': 'User not found'}, status=404)
            
            with connection.cursor() as cursor:
                cursor.callproc('main.update_mfa_setup', [uid, mfa_enabled])
                result = cursor.fetchone()
                if result:
                    user.mfa_enabled = mfa_enabled
                    user.save()
                    return JsonResponse({'success': True})
        else:
            return JsonResponse({'error': 'Invalid request method'}, status=400)
    except Exception as e:
        print(f"Error occurred: {e}")
        return JsonResponse({'error': str(e)}, status=400)


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
                mfa_enabled = result[2]
                attempt.attempts = 0
                attempt.blocked_until = None
                attempt.save()
                user, ucreated = User.objects.get_or_create(user_id = user_id)
                print(f"\n\n\n\n\n{user}")
                user.user_name=user_name
                user.mfa_enabled=mfa_enabled
                user.save()
                request.session['user_id'] = user.user_id
                request.session['logged_in'] = True
                request.session['otp_token'] = False
                messages.success(request, 'Login exitoso!')
                if mfa_enabled:
                    return redirect('mfa_setup')
                else:
                    request.session['otp_token'] = True
                    return redirect('mainMenu')
            else:

                now = datetime.now(tz) 
                if attempt.attempts >= 5:
                    attempt.blocked_until = now + timedelta(minutes=5)
                attempt.save()
                messages.error(request, 'Login fallido!')
                return redirect('loginPage')

    else:
        return redirect('home')
    

class RateLimitedAPIView(APIView):
    """
    Clase base para implementar límites de velocidad en las vistas de la API.

    Atributos:
        rate_limit (int): Número de solicitudes permitidas por minuto.
        rate_timeout (int): Tiempo de espera antes de permitir nuevas solicitudes.

    Métodos:
        dispatch(request, *args, **kwargs): Procesa la solicitud y verifica si se ha superado el límite de velocidad.
    """
    rate_limit = 15
    rate_timeout = 60

    def dispatch(self, request, *args, **kwargs):
        if not self._is_allowed(request):
            return JsonResponse({"message": "Too many requests"}, status=429)
        return super().dispatch(request, *args, **kwargs)

    def _is_allowed(self, request):
        """ Rate-limiting logic using cache. """
        ip = request.META.get("REMOTE_ADDR")
        key = f"rate_limit_{ip}"
        count = cache.get(key, 0)

        if count >= self.rate_limit:
            return False

        cache.set(key, count + 1, timeout=self.rate_timeout)
        return True


class LoginView(RateLimitedAPIView):
    """
    Vista para manejar el login de un usuario.

    Métodos:
        post(request): Procesa la solicitud de login y verifica las credenciales del usuario.
    """
    def post(self, request):
        user_name = request.data.get("user_name")
        password = request.data.get("password")

        attempt, _ = LoginAttempt.objects.get_or_create(username=user_name)
        
        
        if attempt.is_blocked():
            return Response({"success": False, "message": f"Bloqueado hasta: {attempt.blocked_until}"}, status=403)

        
        try:
            with connection.cursor() as cursor:
                cursor.callproc("main.login", [user_name, password])
                result = cursor.fetchone()

                if result:
                    user_id, user_name, mfa_enabled = result

                    
                    attempt.attempts = 0
                    attempt.blocked_until = None
                    attempt.save()

                    
                    user, _ = User.objects.get_or_create(user_id=user_id)
                    user.user_name = user_name
                    user.mfa_enabled = mfa_enabled
                    user.save()

                    
                    request.session["user_id"] = user_id
                    request.session["logged_in"] = True
                    request.session["otp_token"] = False
                    request.session.set_expiry(3600)  

                    if mfa_enabled:
                        
                        user_id = request.session.get("user_id")
                        if not user_id:
                            return Response({"message": "Usuario no autenticado"}, status=403)

                        
                        user, created = customUser.objects.get_or_create(user_id=user_id)
                        
                        
                        if not user.mfa_secret:
                            user.mfa_secret = pyotp.random_base32()
                            user.save()

                        
                        otp_uri = pyotp.totp.TOTP(user.mfa_secret).provisioning_uri(
                            name=user.email, issuer_name="CESAR"
                        )
                        qr = qrcode.make(otp_uri)
                        buffer = io.BytesIO()
                        qr.save(buffer, format="PNG")
                        buffer.seek(0)
                        qr_code = base64.b64encode(buffer.getvalue()).decode("utf-8")

                        
                        user.login_validity = datetime.now()
                        user.save()

                        return Response({
                            "success": True,
                            "user_id": user_id,
                            "user_name": user_name,
                            "redirect": "mfa_setup",
                            "qrcode": f"data:image/png;base64,{qr_code}",
                        }, status=200)

                    return Response({
                        "success": True,
                        "user_id": user_id,
                        "user_name": user_name,
                        "redirect": "mfa_setup" if mfa_enabled else "mainMenu",
                        "message": "Login exitoso!",
                    })

                else:
                    
                    attempt.attempts += 1
                    if attempt.attempts >= 5:
                        attempt.blocked_until = datetime.now() + timedelta(minutes=5)  
                    attempt.save()

                    return Response({"success": False, "message": "Login fallido!"}, status=400)
        except DatabaseError as e:
            # Handle database error
            return Response({"success": False, "message": str(e)}, status=500)
            

class MFASetupView(RateLimitedAPIView):
    """
    Vista para configurar la autenticación de dos factores (MFA) para un usuario.

    Métodos:
        get(request): Devuelve un código QR para que el usuario configure la autenticación de dos factores.
    """
    def get(self, request):
        user_id = request.session.get('user_id')
        if not user_id:
            return Response({'message': 'Usuario no autenticado'}, status=403)

        user, created = customUser.objects.get_or_create(user_id=user_id)
        if not user.mfa_secret:
            user.mfa_secret = pyotp.random_base32()
            user.save()

        otp_uri = pyotp.totp.TOTP(user.mfa_secret).provisioning_uri(
            name=user.email, issuer_name="CESAR"
        )

        qr = qrcode.make(otp_uri)
        buffer = io.BytesIO()
        qr.save(buffer, format="PNG")
        buffer.seek(0)
        qr_code = base64.b64encode(buffer.getvalue()).decode("utf-8")

        user.login_validity = datetime.now()
        user.save()
        print(f"ready to return data:image/png;base64,{qr_code}")
        return Response({"qrcode": f"data:image/png;base64,{qr_code}"}, status=200)
#Unused
class VerifyMFAView(RateLimitedAPIView):
    def post(self, request):
        user_id = request.data.get('user_id')
        otp_code = request.data.get('otp_code')
        print(user_id, otp_code)
        if not user_id:
            return Response({'message': 'User ID is missing'}, status=400)
        if not otp_code:
            return Response({'message': 'OTP code is missing'}, status=400)

        try:
            user = customUser.objects.get(user_id=user_id)
        except customUser.DoesNotExist:
            return Response({'message': 'User not found'}, status=404)

        totp = pyotp.TOTP(user.mfa_secret) 
        if totp.verify(otp_code):
            request.session['otp_token'] = True 
            return Response({'success': True, 'redirect': 'mainMenu'})
        else:
            return Response({'success': False, 'message': 'Invalid OTP'}, status=400)


def get_mfa_status(request):
    """
    Función para obtener el estado de la autenticación de dos factores (MFA) para un usuario.

    Parámetros:
        request (HttpRequest): Solicitud HTTP.

    Retorna:
        dict: Un objeto JSON con el estado de la autenticación de dos factores (MFA) para el usuario.
    """
    uid = request.session.get('user_id') or request.GET.get('user_id') 
    print(f"Checking user_id: {uid}")

    if not uid:
        return JsonResponse({"error": "Unauthorized"}, status=401)

    user = User.objects.filter(user_id=uid).first()
    if not user:
        return JsonResponse({"error": "User not found"}, status=404)

    return JsonResponse({"mfa_enabled": user.mfa_enabled})


class UpdateMFAView(RateLimitedAPIView):
    """
    Vista para actualizar el estado de la autenticación de dos factores (MFA) para un usuario.

    Métodos:
        post(request): Actualiza el estado de la autenticación de dos factores (MFA) para el usuario.
    """
    def post(self, request):
        try:
            uid = request.data.get('user_id')
            mfa_enabled = request.data.get('mfa_enabled')
            if uid is None:
                return JsonResponse({'error': 'User ID not found in session'}, status=400)
            else:
                user = User.objects.filter(user_id=uid).first()
                if not user:
                    return JsonResponse({'error': 'User not found'}, status=404)
                
                with connection.cursor() as cursor:
                    cursor.callproc('main.update_mfa_setup', [uid, mfa_enabled])
                    result = cursor.fetchone()
                    if result:
                        user.mfa_enabled = mfa_enabled
                        user.save()
                        return JsonResponse({'success': True})
        except Exception as e:
            print(f"Error occurred: {e}")
            return JsonResponse({'error': str(e)}, status=400)
        

class RegisterView(RateLimitedAPIView):
    """
    Vista para registrar un nuevo usuario.

    Métodos:
        post(request): Procesa la solicitud de registro y crea un nuevo usuario.
    """
    def post(self, request):
        user_name = request.data.get('user_name')
        password = request.data.get('password')
        print(f"REGISTERING {user_name}, {password}")
        with connection.cursor() as cursor:
            cursor.callproc('main.insupdate_user', [str(user_name), str(password)])
            result = cursor.fetchone()

            if result:
                user_id, user_name, mfa_enabled = result

                user, _ = User.objects.get_or_create(user_id=user_id)
                user.user_name = user_name
                user.mfa_enabled = mfa_enabled
                user.save()

                
                request.session['user_id'] = user_id
                request.session['logged_in'] = True
                request.session['otp_token'] = False  
                
                return Response({
                    'success': True,
                    "user_id": user_id,
                    "user_name": user_name,
                    'redirect': 'mainMenu',
                    'message': 'Usuario agregado!'
                })
            else:
                return Response({'success': False, 'message': 'Login fallido!'}, status=400)