# account/models.py
from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    USER_ROLES = (
        ('customer', 'Покупатель'),
        ('site_admin', 'Администратор сайта'),
        ('superuser', 'Суперпользователь'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=USER_ROLES, default='customer')

    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"