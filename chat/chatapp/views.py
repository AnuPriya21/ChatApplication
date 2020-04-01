from django.shortcuts import render, redirect
from django.contrib.auth.models import User, auth
from django.contrib import messages
from .models import Registration
from django.http import HttpResponse
from .serializer import LoginSerializer, RegistrationSerializer,EmailSerializer,ResetPasswordSerializer
from rest_framework.generics import GenericAPIView
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from chatapp.token import token_activation
from rest_framework.response import Response
from django.contrib.auth import authenticate
from django.http import HttpResponse, HttpResponseRedirect,response
from rest_framework.renderers import JSONRenderer
from rest_framework.renderers import TemplateHTMLRenderer
import jwt
from chat.settings import SECRET_KEY, AUTH_ENDPOINT,JWT_AUTH
from django_short_url.views import get_surl
from django.core.mail import send_mail
from chat.settings import EMAIL_HOST_USER
from validate_email import validate_email
from django.core.mail import EmailMultiAlternatives
from django.core.mail import EmailMessage
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.contrib import messages
from django_short_url.models import ShortURL
from django.conf import settings
import json

class Login(GenericAPIView):
  
    serializer_class = LoginSerializer
    def get(self, request):
        return render(request, 'user/index.html')

    def post(self,request):
       
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(username=username, password=password)
        
        if user is not None:
            if user.is_active:
                auth.login(request, user)
                return redirect('/')
            else:
                return HttpResponse("Your account was inactive.")
        else:
            messages.error(request, 'Invalid Username or Password')
            print("Invalid Credentials")
        return redirect("/")

class Registrations(GenericAPIView):
    
    serializer_class = RegistrationSerializer
    
    def get(self, request):
        return render(request, 'user/registration.html')

    def post(self,request, *args,**kwargs):
        
        name = request.POST.get('name')
        email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get('password')
        password1 = request.POST.get('password2')
        

        if password == password1:
            print("hi")
            user = User.objects.create_user(email=email,username=username, password=password)
            user.save() 
            print("Registered Successfully")
            token = token_activation(username, password)
            print('return from tokens.py:', token)
            current_site = get_current_site(request)
            domain = current_site.domain 
            print(current_site)
            print('domain:', domain)                
            token = token_activation(username, password)
            print('return from tokens.py:', token)
            url = str(token)
            print('url is ',  url)
            surl = get_surl(url)
            print("surl = {}".format(surl))
            z = surl.split("/")
            print("the z value is", z)
            print("z[2] line printed :", z[2])
            mail_subject = "Activate your account clicking on the link below"
            print(mail_subject)
            message = render_to_string('user/emailvalidation.html', {
                    'user': user.username,
                    'domain': domain,
                    'surl': z[2]
            })
            rep = email
            print(message)
            email = EmailMessage(mail_subject, message, to=[rep])
            email.send()
            return HttpResponse('confirmation mail sent!!! Please confirm your email address to complete the registration')
            return redirect("/Login/")
            messages.success(request, 'Your Account has been successfully Activated!!!')
            
        else:
            messages.error(request, 'Invalid Username or Password')
            print("Password didn match")
            return redirect("/registration/from django.shortcuts import render")

def chatapp(request):
    return render(request, 'user/chatapp.html')

def activate(request,surl):
    print("Activate url is ", surl)   
    try:
        tokenobject = ShortURL.objects.get(surl=surl)
        token = tokenobject.lurl
        decode = jwt.decode(token, SECRET_KEY)
        username = decode['username']
        user = User.objects.get(username=username)
        if user is not None:
            user.is_active = True
            user.save()
            messages.info(request, "your account is active now")
            return redirect("/Login/")      
        else:           
            messages.info(request, 'was not able to sent the email')          
            return redirect("/registration/")
    
    except KeyError:
        messages.info(request, 'was not able to sent the email')
        return redirect("/registration/")

class ForgotPassword(GenericAPIView):
    serializer_class = ResetPasswordSerializer
    
    def get(self,request):
        return render(request,'user/forgot_password.html')

    def post(self,request):
        email = request.data['email']
        validate_email(email)

        try:
            user = User.objects.filter(email=email)
            useremail = user.values()[0]['email']
            username = user.values()[0]["username"]
            id = user.values()[0]["id"]

            if useremail is not None:
                token = token_activation(username,id)

                url = str(token)
                surl = get_surl(url)
                slug_url = surl.split('/')
                mail_subject = "reset your account password by clicking below link"
                mail_message = render_to_string('user/resetpassword.html', {
                    'user': username,
                    'domain': get_current_site(request).domain,
                    'surl': slug_url[2]
                })
                print(mail_message)
                recipientemail = useremail
                email = EmailMessage(mail_subject, mail_message, to=[recipientemail])
                email.send()
                return HttpResponse('confirmation mail sent!!!Click on the link to change password')
                return redirect("/login/")
        except TypeError:
            print("User dosent exists")


def resetpassword(request, surl):
    
    try:
        tokenobject = ShortURL.objects.get(surl=surl)
        token = tokenobject.lurl
        decode = jwt.decode(token, SECRET_KEY)
        username = decode['username']
        user = User.objects.get(username=username)

        if user is not None:
            return redirect('/newpassword/' + str(user))
        else:
            return redirect('/forgot_password/')
    except KeyError:
        return HttpResponse("Key Error")



class newpassword(GenericAPIView):
    
    serializer_class = ResetPasswordSerializer

    def post(self,request,user_reset):
        password = request.POST.get('password')
        try:
            user = User.objects.get(username=user_reset)
            user.set_password(password)
            user.save()
            return redirect('/login/')

        except KeyError:
            return HttpResponse("Key Error")
    
def session(request):
  
    return render(request, 'user/session.html')