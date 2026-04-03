from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.dispatch import receiver
from .models import AuditLog
from .security import detect_failed_logins


@receiver(user_logged_in)
def log_login(sender, request, user, **kwargs):
    AuditLog.objects.create(
        user=user,
        action_type="LOGIN",
        description="User logged in",
        ip_address=request.META.get("REMOTE_ADDR"),
    )


@receiver(user_logged_out)
def log_logout(sender, request, user, **kwargs):
    AuditLog.objects.create(
        user=user,
        action_type="LOGOUT",
        description="User logged out",
    )


@receiver(user_login_failed)
def log_failed_login(sender, credentials, request, **kwargs):
    AuditLog.objects.create(
        action_type="FAILED_LOGIN",
        description=f"Failed login: {credentials.get('username')}",
        ip_address=request.META.get("REMOTE_ADDR") if request else None,
    )

    detect_failed_logins()