from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.utils import user_email
from allauth.socialaccount.models import SocialLogin,SocialAccount
from allauth.account.models import EmailAddress
from . models import Usercutsom
from django.db.models import F
from allauth.exceptions import ImmediateHttpResponse
from django.shortcuts import render,redirect
from django.http import HttpResponseForbidden
from django.contrib import messages
from django.contrib.auth import logout,login
from django.contrib.auth import get_user_model


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
            user = sociallogin.user
            if user.is_logged_in:
                    messages.error(request, "User is already logged in elsewhere.")
                    #return HttpResponseForbidden("User is already logged in elsewhere.")
                    
                    raise ImmediateHttpResponse(redirect('login'))
                
            user.is_learner = True
            user.is_logged_in =True
           
            email = sociallogin.account.extra_data.get('email')
            user.username = email.split('@')[0]
            
            try:
                existing_user = Usercutsom.objects.get(username=user.username)
                #user.is_logged_in = True
                existing_user.is_logged_in = True
                existing_user.save()
                sociallogin.connect(request, existing_user)
                #user.save()
                
                
            except Usercutsom.DoesNotExist:
                user.email = email
                user.save() 
            
           
           
            