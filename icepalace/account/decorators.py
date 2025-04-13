# account/decorators.py
from django.core.exceptions import PermissionDenied
from .models import UserProfile


def site_admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            raise PermissionDenied
        if not hasattr(request.user, 'userprofile'):
            raise PermissionDenied
        if request.user.userprofile.role not in ['site_admin', 'superuser']:
            raise PermissionDenied
        return view_func(request, *args, **kwargs)

    return wrapper
