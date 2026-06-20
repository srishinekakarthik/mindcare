from .permissions import get_profile


def user_context(request):
    """
    Injects the authenticated user's real role (from the DB, not localStorage)
    into every template's context so base.html can render role-correct nav
    without trusting client-side state.
    """
    if not request.user.is_authenticated:
        return {
            'user_role': None,
            'user_profile_obj': None,
            'user_institution_name': None,
        }

    profile = get_profile(request.user)
    if not profile:
        return {
            'user_role': None,
            'user_profile_obj': None,
            'user_institution_name': None,
        }

    return {
        'user_role': 'admin' if profile.is_admin else profile.role,
        'user_profile_obj': profile,
        'user_institution_name': profile.institution.name if profile.institution else None,
    }
