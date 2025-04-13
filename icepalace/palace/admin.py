from django.contrib import admin
from django.contrib.admin import AdminSite
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin

from account.models import UserProfile
from .models import Category, Product, Shedule
from django.urls import reverse
from django.utils.html import format_html

AdminSite.site_header = "Администрирование Ледового Дворца"
AdminSite.site_title = "Ледовый Дворец"
AdminSite.index_title = "Управление контентом"


class CustomModelAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(is_active=True)  # Пример фильтрации

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


class CustomAdminMixin:
    def has_delete_permission(self, request, obj=None):
        # Запрещаем удаление для администраторов сайта
        if request.user.groups.filter(name='Site Administrators').exists():
            return False
        return super().has_delete_permission(request, obj)

    def get_readonly_fields(self, request, obj=None):
        # Делаем некоторые поля только для чтения
        if request.user.groups.filter(name='Site Administrators').exists():
            return ['created', 'updated']
        return super().get_readonly_fields(request, obj)


# Инлайн для профиля пользователя
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Дополнительная информация'
    fields = ('role',)


# Кастомный UserAdmin
class CustomUserAdmin(UserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_role')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'userprofile__role')

    def get_role(self, obj):
        if hasattr(obj, 'userprofile'):
            return obj.userprofile.get_role_display()
        return "Покупатель"

    get_role.short_description = 'Роль'


# Перерегистрируем UserAdmin
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


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

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.groups.filter(name='Site Administrators').exists():
            return qs.filter(available=True)
        return qs


@admin.register(Shedule)
class SheduleAdmin(admin.ModelAdmin):
    list_display = ('name', 'time_event', 'slug', 'view_on_site')
    list_filter = ('time_event',)
    search_fields = ('name', 'slug')
    ordering = ('-time_event',)
    date_hierarchy = 'time_event'
    prepopulated_fields = {'slug': ('name',)}

    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'time_event')
        }),
        ('Дополнительная информация', {
            'classes': ('collapse',),
            'fields': (),
        }),
    )

    def view_on_site(self, obj):
        if obj.id and obj.slug:
            return obj.get_absolute_url()
        return None

    view_on_site.short_description = "Просмотреть на сайте"

    def admin_link(self, obj):
        if obj.id:
            url = reverse('admin:palace_shedule_change', args=[obj.id])
            return format_html('<a href="{}">Редактировать</a>', url)
        return ""

    admin_link.short_description = "Действия"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related()

    def save_model(self, request, obj, form, change):
        if not obj.slug:
            from django.utils.text import slugify
            obj.slug = slugify(obj.name)
        super().save_model(request, obj, form, change)
