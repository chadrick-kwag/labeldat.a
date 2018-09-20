from django.shortcuts import render
from django.contrib.auth import login as authlogin, authenticate
from django.contrib.auth.views import LogoutView
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UsernameField
from django import forms
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse

from django.contrib.auth.models import User

import sys, random


# Create your views here.

class customAuthenticationForm(AuthenticationForm):
    username = UsernameField(
        max_length=254,
        widget=forms.TextInput(attrs={'autofocus': True,'placeholder':"username"}),
    )
    password = forms.CharField(
        label=("Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={'placeholder':"username"}),
    )
    

def login(request):
    if request.method=="POST":
        
        username = request.POST.get('username')
        raw_password = request.POST.get('password')

        print("username={},password={}".format(username,raw_password),file=sys.stderr)
        
        user = authenticate(username=username, password=raw_password)
        print("authentication result user={}".format(user),file=sys.stderr)
        authlogin(request, user)
        return HttpResponseRedirect(reverse('myworks'))
        

    else:
        form= customAuthenticationForm()
        return render(request,'login.html',{'form':form})


def generate_random_guestname():
    random.seed()
    index = random.randint(0,30000)
    return "guset{}".format(index)

def fetch_new_guestname():
    tempguestname = generate_random_guestname()
    if check_if_Username_isOccupied(tempguestname):
        print("looping fetch new guestname")
        return fetch_new_guestname()
    return tempguestname
        

def check_if_Username_isOccupied(givenusername):
    result = User.objects.filter(username=givenusername)
    print("check user duplicate result = {}".format(result))
    if len(result) is not 0:
        return True
    return False


def loginasguest(request):
    if request.method=="GET":

        # create guest account

        # randomly generate guest user name
        newguestname = fetch_new_guestname()

        print("created new guest user= {}".format(newguestname))
             
        newguestpw = "{}pw".format(newguestname)


        tempuser = User.objects.create_user(newguestname,'',newguestpw)

        user =authenticate(username=newguestname,password=newguestpw)
        authlogin(request,user)
        return HttpResponseRedirect(reverse('myworks'))
    else:
        form= customAuthenticationForm()
        return render(request,'login.html',{'form':form})
            
def logout(request):
    return HttpResponse("logout")

class customlogoutview(LogoutView):
    pass
