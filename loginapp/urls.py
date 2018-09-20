from django.contrib import admin
from django.urls import path,include

from loginapp import views

urlpatterns = [
    path('login/', views.login,name='login'),
    path('login/guest', views.loginasguest,name='loginguest'),
    path('logout/',views.customlogoutview.as_view(),name='logout'),
    
]