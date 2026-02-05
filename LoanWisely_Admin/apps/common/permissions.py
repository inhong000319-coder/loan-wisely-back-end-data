ROLE_POLICY_WRITER = "POLICY_WRITER"
ROLE_POLICY_APPROVER = "POLICY_APPROVER"
ROLE_AUDITOR = "AUDITOR"
ROLE_SUPER_ADMIN = "SUPER_ADMIN"


def has_role(request, *roles) -> bool:
    actor_roles = getattr(request, "actor_roles", [])
    return any(role in actor_roles for role in roles)


def require_roles(*roles):
    def _decorator(view_func):
        def _wrapped(request, *args, **kwargs):
            if not has_role(request, *roles):
                from django.shortcuts import render
                return render(request, "base/forbidden.html", status=403)
            return view_func(request, *args, **kwargs)
        return _wrapped
    return _decorator


def can_write_policy(request) -> bool:
    return has_role(request, ROLE_POLICY_WRITER, ROLE_SUPER_ADMIN)


def can_approve_policy(request) -> bool:
    return has_role(request, ROLE_POLICY_APPROVER, ROLE_SUPER_ADMIN)


def can_view_audit(request) -> bool:
    return has_role(request, ROLE_AUDITOR, ROLE_SUPER_ADMIN)
