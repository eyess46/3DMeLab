from django.urls import path
from .views_api import (
    RegisterView, VerifyCodeView, LoginView, LogoutView,
    GoogleLoginView, FacebookLoginView
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='api-register'),
    path('verify/', VerifyCodeView.as_view(), name='api-verify'),
    path('login/', LoginView.as_view(), name='api-login'),
    path('logout/', LogoutView.as_view(), name='api-logout'),
    path('social/google/', GoogleLoginView.as_view(), name='google-login'),
    path('social/facebook/', FacebookLoginView.as_view(), name='facebook-login'),
]