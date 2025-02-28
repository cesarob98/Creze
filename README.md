# Creze
 Creze MFA


Se instalo django_ratelimit para limitar los requests por 5 al minuto
Se instalo django-axes para prevenri brute force
	Se añadió 
    'axes', a INSTALLED_APPS
    Y estas 2 propiedades
    AXES_FAILURE_LIMIT = 5  # Max failed attempts before lockout
	AXES_COOLOFF_TIME = 1  # Time in hours before the user can retry

Se utiliza django.middleware.security.SecurityMiddleware'
Se utiliza Cross-Origin Resource Sharing (CORS) Para configurar un único trusted access
	CORS_ALLOWED_ORIGINS = [
	    "http://localhost:3000",
	]

Se añade procedencia de la certificación de CSRF
	CSRF_TRUSTED_ORIGINS = [
	    'http://localhost:3000',
	]