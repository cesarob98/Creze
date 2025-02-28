from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser, Group, Permission 
from django.utils.translation import gettext_lazy as _
import pytz
from datetime import datetime, timedelta
tz = pytz.timezone('America/Mexico_City')

class customUser(models.Model):
    user_id = models.IntegerField(primary_key=True, default=1)
    mfa_secret = models.CharField(max_length=32, blank=True, null=True)
    login_validity = models.DateTimeField(default=timezone.now)
    email = models.CharField(max_length=255, blank=True, null=True)

    def login_is_valid(self):
        now = datetime.now(tz)
        return self.login_validity + timedelta(minutes=5) > now
    def __str__(self):
        return self.email

class LoginAttempt(models.Model):
    username = models.CharField(max_length=255)
    attempts = models.IntegerField(default=0)
    last_attempt = models.DateTimeField(default=timezone.now)
    blocked_until = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        now = datetime.now(tz)
        return f"user={self.username}, attempts={self.attempts}, last_attempt={self.last_attempt}, blockeduntil={self.blocked_until} ---- now => {now}"

    def is_blocked(self):
        now = datetime.now(tz)
        return self.blocked_until and self.blocked_until > now

class User(models.Model):
    user_id = models.AutoField(primary_key=True)
    user_name = models.CharField(max_length=255)
    mfa_enabled = models.BooleanField(default=True)
    password = models.CharField(max_length=255, default='1')

    def __str__(self):
        return f"{self.user_id}:{self.user_name} mfa_enabled => {self.mfa_enabled}"


    