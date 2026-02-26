from django.urls import path
from . import views
from .views import *


urlpatterns = [
path('', views.index, name='index'),
path('contact', views.contact, name = 'contact'),
path('about', views.about, name = 'about'),
path('category', views.category, name = 'category'),



]