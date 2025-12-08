from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils import timezone
from django.contrib.auth.hashers import make_password
from datetime import timedelta
import uuid

from .manager import CustomUserManager


# Custom User Model
class CustomUser(AbstractBaseUser, PermissionsMixin):
    id = models.BigAutoField(primary_key=True)
    email = models.EmailField(unique=True, max_length=255)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)

    # For Role
    ROLES = [
        ('Admin', 'Admin'), 
        ('Manager', 'Manager'),
        ('Technician', 'Technician'),
        ('Customer', 'Customer'),
        ('HR', 'HR'),
    ]
    
    role = models.CharField(max_length=20, choices=ROLES, default='Customer')

    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name", "role"]

    objects = CustomUserManager()

    def __str__(self):
        return f"{self.email}"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    

# Email 
class EmailOTP(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='email_otps')
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    class Meta:
        indexes = [
            models.Index(fields=['user', 'code']),
        ]

    def is_expired(self, expiry_minutes=10):
        return self.created_at + timedelta(minutes=expiry_minutes) < timezone.now()

    def __str__(self):
        return f"{self.user.email} - {self.code}"   


# Password ResetToken 
class PaswordResetToken(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    token_hash = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    used = models.BooleanField(default=False)

    def is_expired(self):
        return timezone.now() > self.created_at + timedelta(minutes=10)
    
    @classmethod
    def generate(cls, user):
        raw_token = uuid.uuid4().hex
        hashed = make_password(raw_token)
        obj = cls.objects.create(user=user, token_hash=hashed)

        return raw_token, obj
    