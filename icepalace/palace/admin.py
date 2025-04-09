from django.contrib import admin
from .models import Category, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'price',
                    'available', 'created', 'updated']  # for display
    list_filter = ['available', 'created', 'updated']  # for filter
    list_editable = ['price', 'available']  # for editable field
    prepopulated_fields = {'slug': ('name',)}  # auto generate slug
