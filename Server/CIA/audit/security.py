from django.utils.timezone import now, timedelta
from .models import AuditLog

def detect_failed_logins():
    last_5_min = now() - timedelta(minutes=5)

    attempts = AuditLog.objects.filter(
        action_type="FAILED_LOGIN",
        timestamp__gte=last_5_min
    ).count()

    if attempts > 5:
        print("⚠️ ALERT: Possible brute force attack")
    return attempts > 5   