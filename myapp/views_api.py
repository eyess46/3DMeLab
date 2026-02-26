from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate, login, logout
from django.core.mail import send_mail
from django.conf import settings
from .models import User, VerificationCode
from .serializers import RegisterSerializer, VerifySerializer, LoginSerializer
from rest_framework.permissions import IsAuthenticated
import requests


from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator



def generate_otp():
    from django.utils.crypto import get_random_string
    return get_random_string(length=6, allowed_chars='0123456789')


def send_verification_email(email, code):
    subject = 'Your Verification Code'
    message = f'Your verification code is: {code}\nExpires in 20 minutes.'
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])



@method_decorator(csrf_exempt, name='dispatch')
class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            VerificationCode.objects.filter(user=user).delete()

            code = generate_otp()
            verification = VerificationCode(user=user)
            verification.set_code(code)
            send_verification_email(user.email, code)

            return Response({"message": "Verification code sent to your email."})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(csrf_exempt, name='dispatch')
class VerifyCodeView(APIView):
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
                    return Response({"message": "Email verified successfully!"})
                else:
                    verification.attempts += 1
                    verification.save()
                    if verification.attempts >= 5:
                        verification.delete()
                        return Response(
                            {"error": "Too many attempts, please register again."},
                            status=status.HTTP_400_BAD_REQUEST
                        )
                    return Response({"error": "Invalid or expired code."},
                                    status=status.HTTP_400_BAD_REQUEST)
            except User.DoesNotExist:
                return Response({"error": "No pending registration found."},
                                status=status.HTTP_400_BAD_REQUEST)
            except VerificationCode.DoesNotExist:
                return Response({"error": "Verification session expired."},
                                status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(csrf_exempt, name='dispatch')
class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = authenticate(
                email=serializer.validated_data['email'],
                password=serializer.validated_data['password']
            )
            if user:
                if not user.is_active:
                    return Response(
                        {"error": "Please verify your email first."},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                login(request, user)
                return Response({"message": "Login successful.", "email": user.email})
            return Response({"error": "Invalid credentials."},
                            status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(csrf_exempt, name='dispatch')
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        logout(request)
        return Response({"message": "Logout successful."}, status=status.HTTP_200_OK)




@method_decorator(csrf_exempt, name='dispatch')
class GoogleLoginView(APIView):
    def post(self, request):
        access_token = request.data.get('access_token')
        if not access_token:
            return Response({'error': 'Access token required'},
                            status=status.HTTP_400_BAD_REQUEST)

        # Verify token with Google API
        url = f'https://www.googleapis.com/oauth2/v3/userinfo?access_token={access_token}'
        resp = requests.get(url)
        if resp.status_code != 200:
            return Response({'error': 'Invalid Google token'},
                            status=status.HTTP_400_BAD_REQUEST)

        data = resp.json()
        email = data.get('email')
        if not email:
            return Response({'error': 'No email returned from Google'},
                            status=status.HTTP_400_BAD_REQUEST)

        user, created = User.objects.get_or_create(email=email, defaults={'is_active': True})
        login(request, user)
        return Response({'message': 'Google login successful', 'email': user.email})


@method_decorator(csrf_exempt, name='dispatch')
class FacebookLoginView(APIView):
    def post(self, request):
        access_token = request.data.get('access_token')
        if not access_token:
            return Response({'error': 'Access token required'},
                            status=status.HTTP_400_BAD_REQUEST)

        # Verify token with Facebook API
        url = f'https://graph.facebook.com/me?fields=id,name,email&access_token={access_token}'
        resp = requests.get(url)
        if resp.status_code != 200:
            return Response({'error': 'Invalid Facebook token'},
                            status=status.HTTP_400_BAD_REQUEST)

        data = resp.json()
        email = data.get('email')
        if not email:
            return Response({'error': 'No email returned from Facebook'},
                            status=status.HTTP_400_BAD_REQUEST)

        user, created = User.objects.get_or_create(email=email, defaults={'is_active': True})
        login(request, user)
        return Response({'message': 'Facebook login successful', 'email': user.email})