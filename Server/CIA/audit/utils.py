from .models import AuditLog


def log_action(
    user=None,
    action_type="API_CALL",
    description="",
    resource=None,
    resource_id=None,
    request=None,
    old_data=None,
    new_data=None,
):
    AuditLog.objects.create(
        user=user,
        action_type=action_type,
        description=description,
        resource=resource,
        resource_id=resource_id,

        ip_address=request.META.get("REMOTE_ADDR") if request else None,
        user_agent=request.META.get("HTTP_USER_AGENT") if request else None,
        request_method=request.method if request else None,
        endpoint=request.path if request else None,

        old_data=old_data,
        new_data=new_data,
    )