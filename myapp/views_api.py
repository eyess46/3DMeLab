from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.core.mail import send_mail
from django.conf import settings
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import User, VerificationCode
from .serializers import RegisterSerializer, VerifySerializer, LoginSerializer
from django.utils.crypto import get_random_string
import requests



def generate_otp():
    return get_random_string(length=6, allowed_chars='0123456789')


def send_verification_email(email, code):
    subject = 'Your Verification Code'
    message = f'Your verification code is: {code}\n\nIt expires in 20 minutes.'
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])



class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save(is_active=False)
            VerificationCode.objects.filter(user=user).delete()

            code = generate_otp()
            verification = VerificationCode(user=user)
            verification.set_code(code)
            send_verification_email(user.email, code)

            return Response({'message': 'Verification code sent to your email.'}, status=201)
        return Response(serializer.errors, status=400)


class VerifyCodeView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = VerifySerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            code = serializer.validated_data['code']
            try:
                user = User.objects.get(email=email, is_active=False)
                verification = VerificationCode.objects.get(user=user)
                if verification.check_code(code):
                    user.is_active = True
                    user.save()
                    verification.delete()
                    token, _ = Token.objects.get_or_create(user=user)
                    return Response({'message': 'Email verified successfully!', 'token': token.key})
                else:
                    return Response({'error': 'Invalid or expired code.'}, status=400)
            except (User.DoesNotExist, VerificationCode.DoesNotExist):
                return Response({'error': 'Invalid verification request.'}, status=400)
        return Response(serializer.errors, status=400)



class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            user = authenticate(request, email=email, password=password)
            if user and user.is_active:
                token, _ = Token.objects.get_or_create(user=user)
                return Response({'message': 'Login successful', 'token': token.key, 'email': user.email})
            return Response({'error': 'Invalid credentials or unverified account.'}, status=400)
        return Response(serializer.errors, status=400)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        Token.objects.filter(user=request.user).delete()
        return Response({'message': 'Logout successful.'}, status=200)



class GoogleLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        access_token = request.data.get('access_token')
        if not access_token:
            return Response({'error': 'Access token required'}, status=400)

        url = f'https://www.googleapis.com/oauth2/v3/userinfo?access_token={access_token}'
        resp = requests.get(url)
        if resp.status_code != 200:
            return Response({'error': 'Invalid Google token'}, status=400)

        data = resp.json()
        email = data.get('email')
        if not email:
            return Response({'error': 'No email returned from Google'}, status=400)

        user, _ = User.objects.get_or_create(email=email, defaults={'is_active': True})
        token, _ = Token.objects.get_or_create(user=user)
        return Response({'message': 'Google login successful', 'token': token.key, 'email': user.email})



class FacebookLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        access_token = request.data.get('access_token')
        if not access_token:
            return Response({'error': 'Access token required'}, status=400)

        url = f'https://graph.facebook.com/me?fields=id,name,email&access_token={access_token}'
        resp = requests.get(url)
        if resp.status_code != 200:
            return Response({'error': 'Invalid Facebook token'}, status=400)

        data = resp.json()
        email = data.get('email')
        if not email:
            return Response({'error': 'No email returned from Facebook'}, status=400)

        user, _ = User.objects.get_or_create(email=email, defaults={'is_active': True})
        token, _ = Token.objects.get_or_create(user=user)
        return Response({'message': 'Facebook login successful', 'token': token.key, 'email': user.email})