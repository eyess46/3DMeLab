from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from django.utils.crypto import get_random_string
from .forms import RegistrationForm, EmailAuthenticationForm
from .models import User, VerificationCode
from django.views.decorators.cache import never_cache

# Create your views here.

def index(request):
    
    
    return render(request, 'index.html')

   
   
def contact(request):
   
   if request.method == "POST":                    
        name = request.POST.get('name')      
        email = request.POST.get('email')        
        subject = request.POST.get('subject') 
        message = request.POST.get('message')            
                       
                    
        Contactform.objects.create(name=name, email=email, subject=subject, message=message,)
        messages.success(request, f'Your Message Has Been Sent Successfully!')       
        return redirect('index')  

   else:
      return render(request, 'contact.html', )
    

def about(request):
    
    return render(request, 'about.html')

def category(request):
    
    return render(request, 'category.html')    