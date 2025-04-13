from django.urls import path, include
from django.contrib.auth import views as auth_views

import palace
from palace import views
from . import views
from .views import admin_dashboard

urlpatterns = [
    #path('login/', views.user_login, name='login'),
    # path('login/', auth_views.LoginView.as_view(), name='login'),
    #path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    path('', include('django.contrib.auth.urls')),
    #path('palace/', palace.views.home, name='home'),
    path('admin-dashboard/', admin_dashboard, name='admin_dashboard'),
]
