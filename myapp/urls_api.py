from django.urls import path
from .views_api import (
    RegisterView, VerifyCodeView, LoginView, LogoutView,
    GoogleLoginView, FacebookLoginView,
)

urlpatterns = [
    path("register/", RegisterView.as_view()),
    path("verify/", VerifyCodeView.as_view()),
    path("login/", LoginView.as_view()),
    path("logout/", LogoutView.as_view()),
    path("social/google/", GoogleLoginView.as_view()),
    path("social/facebook/", FacebookLoginView.as_view()),
]