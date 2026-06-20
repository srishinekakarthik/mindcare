"""
Centralized role-checking helpers.

The platform has 4 roles (UserProfile.role): student, staff, counselor, admin.
- student / staff belong to an Institution.
- counselor / admin serve every institution and have no Institution tie.
- counselor accounts require UserProfile.is_approved before they can use
  counselor-only features (set by an admin).
"""
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from .models import UserProfile


def get_profile(user):
    """Return the UserProfile for a user, or None if it doesn't exist."""
    try:
        return user.userprofile
    except UserProfile.DoesNotExist:
        return None


def role_required(*allowed_roles, require_approved=False):
    """
    View decorator restricting access to specific roles.
    Admins (role='admin' or is_superuser) always pass, regardless of allowed_roles,
    unless explicitly excluded isn't supported (admins are platform-wide superusers).
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapped(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')

            profile = get_profile(request.user)
            if profile is None:
                messages.error(request, 'User profile not found')
                return redirect('login')

            if profile.is_admin:
                return view_func(request, *args, **kwargs)

            if profile.role not in allowed_roles:
                messages.error(request, 'Access denied for your account type.')
                return redirect('mindcare_home')

            if require_approved and profile.role == 'counselor' and not profile.is_approved:
                messages.error(request, 'Your counselor account is pending admin approval.')
                return redirect('mindcare_home')

            return view_func(request, *args, **kwargs)
        return wrapped
    return decorator
