from django.urls import path
from . import views


app_name = 'palace'

urlpatterns = [

    path('', views.home, name='home'),
    path('shedule/', views.shedule_list, name='shedule_list'),
    path('shedule/<int:id>/<slug:slug>/', views.shedule_detail, name='shedule_detail'),
    path('products/', views.product_list, name='product_list'),
    path('products/<slug:category_slug>/', views.product_list, name='product_list_by_category'),
    path('product/<int:id>/<slug:slug>/', views.product_detail, name='product_detail'),



]
