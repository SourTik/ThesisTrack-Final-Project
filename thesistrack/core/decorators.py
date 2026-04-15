from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied


def role_required(*roles):
    """Allow only authenticated users with one of the provided roles."""
    allowed_roles = set(roles)

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            user_role = getattr(request.user, 'role', None)
            if user_role not in allowed_roles:
                raise PermissionDenied('You are not allowed to access this resource.')
            return view_func(request, *args, **kwargs)

        return login_required(_wrapped_view)

    return decorator
