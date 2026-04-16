from functools import wraps

from django.contrib import messages
from django.shortcuts import redirect


def role_required(*allowed_roles):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('accounts:login')
            if request.user.role not in allowed_roles and not request.user.is_superuser:
                messages.error(request, 'You do not have permission to access this page.')
                return redirect('core:dashboard_redirect')
            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator
