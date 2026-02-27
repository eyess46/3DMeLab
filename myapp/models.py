from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.hashers import make_password, check_password
from django.utils.crypto import get_random_string
from django.utils import timezone
from datetime import timedelta


class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True, verbose_name='email address')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email


class VerificationCode(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    code_hash = models.CharField(max_length=128, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    attempts = models.PositiveSmallIntegerField(default=0)

    def set_code(self, raw_code: str):
        self.code_hash = make_password(raw_code)
        self.created_at = timezone.now()
        self.attempts = 0
        self.save()

    def check_code(self, raw_code: str) -> bool:
        if self.is_expired():
            return False
        return check_password(raw_code, self.code_hash)

    def is_expired(self) -> bool:
        expiry_time = self.created_at + timedelta(minutes=20)
        return timezone.now() > expiry_time

    def __str__(self):
        return f"Code for {self.user.email}"


class Contactform(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=100)
    message = models.TextField()  
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} – {self.email}"