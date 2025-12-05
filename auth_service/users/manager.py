from django.contrib.auth.models import BaseUserManager

class CustomUserManager(BaseUserManager):
    # For User
    def create_user(self, email, first_name=None, last_name=None, role="Customer", password=None, **extra_fields):
        if not email:
            raise ValueError("The Email fields is required")
        
        email = self.normalize_email(email)
        
        user = self.model(
            email = email,
            first_name = first_name,
            last_name = last_name,
            role = role,
            **extra_fields,
        )
        
        user.set_password(password)
        user.save(using=self._db)
        return user

    # For Super User Creation-Admin
    def create_superuser(self, email, first_name, last_name, password=None, **extra_fields):
        extra_fields.setdefault("role", "Admin")
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        # Validate superuser fields
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
         
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(
            email=email, 
            first_name=first_name, 
            last_name=last_name,    
            password=password, 
            **extra_fields
            )   

    

