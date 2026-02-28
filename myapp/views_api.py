from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import authenticate
from django.core.mail import send_mail
from django.conf import settings
from .models import User, VerificationCode
from .serializers import (
    RegisterSerializer,
    VerifySerializer,
    LoginSerializer,
)
from django.utils.crypto import get_random_string
from rest_framework_simplejwt.tokens import RefreshToken
import requests



def generate_otp():
    return get_random_string(6, "0123456789")


def send_verification_email(email, code):
    subject = "Your Verification Code"
    message = f"Your verification code is: {code}\nValid for 20 minutes."
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save(is_active=False)
            VerificationCode.objects.filter(user=user).delete()
            code = generate_otp()
            ver = VerificationCode(user=user)
            ver.set_code(code)
            send_verification_email(user.email, code)
            return Response({"message": "Verification code sent."}, status=201)
        return Response(serializer.errors, status=400)

        return Response(serializer.errors, status=400)


class VerifyCodeView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = VerifySerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data["email"]
            code = serializer.validated_data["code"]
            try:
                user = User.objects.get(email=email, is_active=False)
                ver = VerificationCode.objects.get(user=user)
                if ver.check_code(code):
                    user.is_active = True
                    user.save()
                    ver.delete()
                    return Response({"message": "Verification successful."})
            except (User.DoesNotExist, VerificationCode.DoesNotExist):
                pass
        return Response({"error": "Invalid or expired code."}, status=400)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = authenticate(
                request,
                email=serializer.validated_data["email"],
                password=serializer.validated_data["password"],
            )
            if user and user.is_active:
                refresh = RefreshToken.for_user(user)
                return Response(
                    {
                        "refresh": str(refresh),
                        "access": str(refresh.access_token),
                        "message": "Login successful.",
                    }
                )
        return Response({"error": "Invalid credentials"}, status=400)




class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        
        return Response({"message": "Logout successful."})




class GoogleLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        token = request.data.get("access_token")
        if not token:
            return Response({"error": "Token required"}, status=400)
        url = (
            f"https://www.googleapis.com/oauth2/v3/userinfo?access_token={token}"
        )
        resp = requests.get(url)
        if resp.status_code != 200:
            return Response({"error": "Invalid Google token"}, status=400)
        data = resp.json()
        email = data.get("email")
        if not email:
            return Response({"error": "No email returned"}, status=400)
        user, _ = User.objects.get_or_create(
            email=email, defaults={"is_active": True}
        )
        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "message": "Google login successful.",
            }
        )



class FacebookLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        token = request.data.get("access_token")
        if not token:
            return Response({"error": "Token required"}, status=400)
        url = (
            f"https://graph.facebook.com/me?fields=id,name,email&access_token={token}"
        )
        resp = requests.get(url)
        if resp.status_code != 200:
            return Response({"error": "Invalid Facebook token"}, status=400)
        data = resp.json()
        email = data.get("email")
        if not email:
            return Response({"error": "No email returned"}, status=400)
        user, _ = User.objects.get_or_create(
            email=email, defaults={"is_active": True}
        )
        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "message": "Facebook login successful.",
            }
        )