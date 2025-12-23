from django.db import models, transaction
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils import timezone
from django.contrib.auth.hashers import make_password, check_password
from datetime import timedelta
import uuid

from .manager import CustomUserManager


# Custom User Model
class CustomUser(AbstractBaseUser, PermissionsMixin):
    id = models.BigAutoField(primary_key=True)
    email = models.EmailField(unique=True, max_length=255, db_index=True)
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
    REQUIRED_FIELDS = ["first_name", "last_name"]

    objects = CustomUserManager()

    class Meta:
        db_table = "users_customuser"
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return self.email
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def get_short_name(self):
        return self.first_name
    
    @property
    def full_name(self):
        return self.get_full_name()
    

# Email 
class EmailOTP(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="email_otps")
    code = models.CharField(max_length=6, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    used = models.BooleanField(default=False)

    EXPIRY_MINUTES = 10

    class Meta:
        indexes = [
            models.Index(fields=['user', 'code']),
        ]
        ordering = ["-created_at"]

    def is_expired(self):
        return self.created_at + timedelta(minutes=self.EXPIRY_MINUTES) < timezone.now()

    def mark_used(self):
        self.used = True
        self.save(update_fields=["used"])

    def __str__(self):
        return f"{self.user.email} - {self.code}"   


# Password ResetToken 
class PasswordResetToken(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="password_reset_tokens")
    token_hash = models.CharField(max_length=255, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    used = models.BooleanField(default=False)

    EXPIRY_MINUTES = 10

    class Meta:
        indexes = [
            models.Index(fields=["user", "used"])
        ]
        ordering = ['-created_at']

    def is_expired(self):
        return timezone.now() > self.created_at + timedelta(minutes=self.EXPIRY_MINUTES)
    
    def mark_used(self):
        self.used = True
        self.save(update_fields=["used"])

    @classmethod
    def generate(cls, user):
        with transaction.atomic():
            cls.objects.filter(user=user, used=False).update(used=True)

            raw_token = uuid.uuid4().hex
            hashed = make_password(raw_token)
            obj = cls.objects.create(user=user, token_hash=hashed)

        return raw_token, obj
    
    def verify(self, raw_token):
        if self.used or self.is_expired():
            return False
        return check_password(raw_token, self.token_hash)
    
    def __str__(self):
        return f"Reset token for {self.user.email}"
    