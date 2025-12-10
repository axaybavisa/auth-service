from django.urls import path
from .views import (
    RegisterView,
    VerifyEmailView,
    UserLoginView,
    UserLogoutView,
    TokenRefreshView,
    ChangePasswordView,
    ForgotPasswordView,
    ResetPasswordView,
)

app_name = "auth"

# API v1 URL patterns 
urlpatterns = [
    path("auth/register/", RegisterView.as_view(), name="register"),
    path("auth/verify-email/", VerifyEmailView.as_view(), name="verify-email"),
    path("auth/login/", UserLoginView.as_view(), name="login"),
    path("auth/logout/", UserLogoutView.as_view(), name="logout"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("auth/change-password/", ChangePasswordView.as_view(), name="change-password"),
    path("auth/forgot-password/", ForgotPasswordView.as_view(), name="forgot-password"),
    path("auth/reset-password/", ResetPasswordView.as_view(), name="reset-password"),
    ]