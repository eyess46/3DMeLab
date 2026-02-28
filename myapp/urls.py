from django.urls import path
from . import views
from .views import *
from . import views_api

urlpatterns = [
    path("register/", views_api.RegisterView.as_view(), name="api_register"),
    path("verify/", views_api.VerifyCodeView.as_view(), name="api_verify"),
    path("login/", views_api.LoginView.as_view(), name="api_login"),   # optional;
    path("logout/", views_api.LogoutView.as_view(), name="api_logout"),
    path("google/", views_api.GoogleLoginView.as_view(), name="api_google"),
    path("facebook/", views_api.FacebookLoginView.as_view(), name="api_facebook"),
]