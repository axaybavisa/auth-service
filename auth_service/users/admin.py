from django.contrib import admin
from django.contrib.auth.admin import UserAdmin 
from .models import CustomUser, EmailOTP, PasswordResetToken


# Email OTP - inline
class EmailOTPInline(admin.TabularInline):
    model = EmailOTP
    extra = 0
    readonly_fields = ('code', 'created_at', 'is_used')
    can_delete = False


# Password-reset token - inline
class PasswordResetTokenInline(admin.TabularInline):
    model = PasswordResetToken
    extra = 0
    readonly_fields = ("token_hash", "created_at", "used")


# Register your custom user model with the admin site
class CustomUserAdmin(UserAdmin):
    model = CustomUser

    # Fields that are read-only in the admin interface
    readonly_fields = ('created_at', 'updated_at')

    # Fields to display in the user list view
    list_display =  (
        'id', 'email', 'first_name', 'last_name', 'role',
        'is_active', 'is_staff', 'is_superuser'
    )

    # Fields that link to the user detail view
    list_display_links = ('id', 'email')

    # Filters for the user list view
    list_filter = ('role', 'is_active', 'is_staff', 'is_superuser')
    
    # Fieldsets for the user detail view
    fieldsets = (
        ('Login Credentials', {
            'fields': ('email', 'first_name', 'last_name', 'role', 'password')}),
        
        ('Permissions', {
            'fields': ('is_active','is_staff', 'is_superuser')}),
        
        ('Important dates', {
            'fields': ('last_login', 'created_at', 'updated_at')}),
    )

    # Fieldsets for adding a new user
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'role', 'password', 'is_staff', 'is_active', 'is_superuser')}
        ),
    )

    # Search and ordering options
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)


    inlines = [EmailOTPInline, PasswordResetTokenInline]

# Register the custom user model with the admin site
admin.site.register(CustomUser, CustomUserAdmin)
