# account/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User, Group
from .models import UserProfile





class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Дополнительная информация'


class CustomUserAdmin(UserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'get_role')
    list_filter = ('userprofile__role',)

    def get_role(self, obj):
        return obj.userprofile.get_role_display()

    get_role.short_description = 'Роль'


# Перерегистрируем UserAdmin
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role')
    list_editable = ('role',)
    list_filter = ('role',)
    search_fields = ('user__username', 'user__email')


# Скрываем стандартные модели User и Group для администраторов сайта
class CustomAdminSite(admin.AdminSite):
    def has_permission(self, request):
        if request.user.is_active and (
                request.user.is_superuser or request.user.groups.filter(name='Site Administrators').exists()):
            return True
        return False


custom_admin_site = CustomAdminSite(name='custom_admin')
# Регистрируем модели только для суперпользователей
if admin.site.is_registered(User):
    admin.site.unregister(User)
if admin.site.is_registered(Group):
    admin.site.unregister(Group)


@admin.register(User, site=admin.site)
class UserAdmin(admin.ModelAdmin):
    def has_module_permission(self, request):
        return request.user.is_superuser


@admin.register(Group, site=admin.site)
class GroupAdmin(admin.ModelAdmin):
    def has_module_permission(self, request):
        return request.user.is_superuser
