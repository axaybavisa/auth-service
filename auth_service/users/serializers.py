from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from django.contrib.auth.hashers import check_password

from .models import EmailOTP, PasswordResetToken

# Get the User model
User = get_user_model()

# Serializer for user registration
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8, style={"input_type": "password"})

    class Meta: 
        model = User
        fields = ["id","email", "first_name", "last_name", "role", "password"]       

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate_password(self, value):
        validate_password(value)
        return value
    
    def create(self, validated_data):
        password = validated_data.pop("password")

        user = User.objects.create_user(
            password=password,
            is_active=False,
            **validated_data
        )
        return user
    

# Serializer for empty responses
class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=6)

    def validate(self, data):
        email = data["email"]
        code = data["code"]
        
        # check if user exists
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({"email": "User with this email does not exist."})
        
        # get latest OTP
        try:
            otp = EmailOTP.objects.filter(
                user=user, code=code, is_used=False
            ).latest("created_at")
        except EmailOTP.DoesNotExist:
            raise serializers.ValidationError({"code": "Invalid OTP code."}) 

        # Check OTP expiry
        if otp.is_expired():
            raise serializers.ValidationError({"code": "OTP code has expired."})
        
        data["user"] = user
        data["otp"] = otp
        return data
    
    def save(self, **kwargs):
        user = self.validated_data["user"]
        otp = self.validated_data["otp"]

        #mark otp used
        otp.is_used = True
        otp.save()

        # activate user
        user.is_active = True
        user.save()

        return user


# Serializer for user login
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, style={"input_type": "password"})

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid email or password.")

        if not user.check_password(password):
            raise serializers.ValidationError("Invalid email or password.")

        if not user.is_active:
            raise serializers.ValidationError("User account is not active.")

        data['user'] = user
        return data



# Logout Serializer for JWT tokens
class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def validate(self, data):
        self.token = data["refresh"]
        return data

    def save(self, **kwargs):
        try:
            RefreshToken(self.token).blacklist()
        except TokenError:
            raise serializers.ValidationError({"message": "Invalid or expired token."})
        

# Change Password Serializer
class ChangePasswordSerializer(serializers.ModelSerializer):
    old_password = serializers.CharField(write_only=True, style={"input_type": "password"})
    new_password = serializers.CharField(write_only=True, style={"input_type": "password"})
    confirm_new_password = serializers.CharField(write_only=True, style={"input_type": "password"})
    
    class Meta:
        model = User
        fields = ["old_password", "new_password", "confirm_new_password"]
   
    def validate(self, attrs):
        user = self.context["request"].user

        old_password = attrs.get("old_password")
        new_password = attrs.get("new_password")
        confirm_new_password = attrs.get("confirm_new_password")    

        # Validate old password
        if not user.check_password(old_password):
            raise serializers.ValidationError({"old_password": "Old password is incorrect."})   
        
        # Validate new password and confirmation match
        if new_password != confirm_new_password:
            raise serializers.ValidationError({"confirm_new_password": "New password and confirm password does not match."})
        
        validate_password(new_password, user=user)

        return attrs
    
    def update(self, instance, validated_data):
        new_password = validated_data["new_password"]
        instance.set_password(new_password)
        instance.save()
        return instance
    

# Forgot Password
class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("No User Associated with this Email.")
        return value


# Reset Password
class ResetPasswordSerializer(serializers.Serializer):
    token = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True, required=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        token = attrs.get("token")
        password = attrs.get("password")
        confirm_password = attrs.get("confirm_password")

        # check password
        if password != confirm_password:
            raise serializers.ValidationError({"password": "Passwords do not match"})

        # validate password strength
        validate_password(password)

        # validate the math token in db
        tokens = PasswordResetToken.objects.filter(used=False)
        matched = None

        for obj in tokens:
            if check_password(token, obj.token_hash):
                matched = obj
                break

        if matched is None:
            raise serializers.ValidationError({"token": "Invalid or expired token."})

        # check token expiry    
        if matched.is_expired():
            raise serializers.ValidationError({"token": "Token has expired."})    

        # password validation - send token_obj forward
        attrs["token_obj"] = matched
        
        return attrs
    