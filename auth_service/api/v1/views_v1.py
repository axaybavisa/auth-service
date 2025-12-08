from rest_framework.response import Response
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from django.utils import timezone
from django.contrib.auth.hashers import check_password

from users.models import PaswordResetToken
from users.task import send_otp_via_email, send_password_reset_email 
from users.serializers import(
    RegisterSerializer,
    VerifyOTPSerializer,
    LoginSerializer,
    LogoutSerializer,
    ChangePasswordSerializer,
    ForgotPasswordSerializer,
    ResetPasswordSerializer,
)


# Get the User model
User = get_user_model()

# API view for user registration
class RegisterView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        send_otp_via_email(user)

        return Response(
            {
                "detail": "User created. OTP sent to your email.",
                "email": user.email,
            },
        status=status.HTTP_201_CREATED
        )
    

# API view for email verification
class VerifyEmailView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = VerifyOTPSerializer

    def get(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response(
            {"detail": "Your Email verified successfully."}, 
            status=status.HTTP_200_OK
            )


# Login View to obtain JWT tokens
class UserLoginView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = serializer.validated_data['user']

        refresh = RefreshToken.for_user(user)

        user.last_login = timezone.now()
        user.save(update_fields=["last_login"])

        return Response(
            {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'email': user.email
            },
            status=status.HTTP_200_OK
        )
    

# Logout View to blacklist JWT refresh tokens
class UserLogoutView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = LogoutSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"detail": "Logout successful."}, 
            status=status.HTTP_200_OK
        )
    

# Token Refresh View
class TokenRefreshView(generics.GenericAPIView):
    serializer_class = TokenRefreshSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            return Response(
                {"detail": "Invalid or expired refresh token."}, 
                status=status.HTTP_401_UNAUTHORIZED
            )      
          
        return Response(
            serializer.validated_data, 
            status=status.HTTP_200_OK
        )
    

# Change Password View
class ChangePasswordView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ChangePasswordSerializer

    def post(self, request, *args, **kwargs):
        user = request.user
        serializer = self.get_serializer(instance=user, data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {"detail": "Password updated successfully."}, 
            status=status.HTTP_200_OK
        )


# Forgot Password
class ForgotPasswordView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ForgotPasswordSerializer

    def post(self, request, *args,**kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = User.objects.get(email=serializer.validated_data["email"])

        send_password_reset_email(user)

        return Response(
            {"message": "Password reset link sent to your email."},
            status=status.HTTP_200_OK
        )    

# Reset Password
class ResetPasswordView(generics.GenericAPIView):
    serializer_class = ResetPasswordSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        token = serializer.validated_data["token"]
        new_password = serializer.validated_data["password"]

        # find token
        tokens = PaswordResetToken.objects.filter(used=False)
        for obj in tokens:
            if check_password(token, obj.token_hash):
                if obj.is_expired():
                    return Response({"error": "Token expired."}, status=status.HTTP_400_BAD_REQUEST)
                
                user = obj.user
                user.set_password(new_password)
                user.save

                obj.used = True
                obj.save()
                
                return Response({"message": "Password reset successful."})
            
            return Response({"error": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST)
            

