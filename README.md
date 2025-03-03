# Creze
 Creze MFA

Se crea esta pequeña y sencilla versión de un login en django y en react
Backend en django funciona a manera de API
Frontend en react completando las peticiones a través de certificación Cross-site request forgery con axios

Para la base de datos se seleccionó POSTGRES 17, se creó esquema main
	Se dejan los scripts necesarios para simularla en la carpeta de Database
	La contraseña no se podrá recuperar nunca pero se puede comparar con la que hayas dado de alta previamente
	Para las contraseñas como parte del manejo de datos sensibles se guardan en un campo cifradas con algoritmo blowfish
	la justificación de este es para usar un algoritmo efectivo de cifrado aunque no tan potente como sha1 o md5 pero eficaz para la demostración


Para echarlo a andar
	Backend
		Hecho en django
		Se tiene un virtual environment creado dentro de la ruta CREZE
		Navegar a Creze
		Correr el comando venv\Scripts\activate
		Navegar a \venv\backend en bash
		Correr el comando python migrate.py runserver 
		Y eso correrá el proyecto en http://localhost:8000
	Frontend
		Hecho en react
		Navegar a la ruta reactapp
		Correr en bash npm run start
		Y eso correrá el proyecto en http://localhost:3000

	DB
		Para simularla de manera local se  deberán correr todoos los archivos empezando por tables
		Se tiene la base de datos en AWS RDS
			En creze.c9ussqiak44u.us-east-2.rds.amazonaws.com 




Justificaciones:
	Se añaden las librerías
		qrcode Para generar el QR
		pyotp para hacer la verificación por GOOGLE AUTHENTICATTOR
	Se añade el timezone de CENTRAL TIME
		TIME_ZONE = 'UTC'

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


	En AWS EB se cambian por
		CORS_ALLOWED_ORIGINS = [
			"https://master.d1s89094099o2d.amplifyapp.com",
			"django-env.eba-qkkpspsz.us-west-2.elasticbeanstalk.com"
		]
		CSRF_TRUSTED_ORIGINS = [
			'https://master.d1s89094099o2d.amplifyapp.com',
		]
		mas estas líneas 
		SESSION_COOKIE_NAME = 'sessionid'  
		SESSION_COOKIE_AGE = 1209600 
		SESSION_SAVE_EVERY_REQUEST = True 
		SESSION_EXPIRE_AT_BROWSER_CLOSE = False
		AXES_FAILURE_LIMIT = 5
		AXES_COOLOFF_TIME = 1
		Backend running on 
		http://django-env.eba-qkkpspsz.us-west-2.elasticbeanstalk.com


	Se añaden pruebas unitarias en authenticator/tests
		Se corren con este comando
		python manage.py test authenticator.tests --keepdb