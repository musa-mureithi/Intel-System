from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from audit.models import AuditLog


class Command(BaseCommand):
    help = "Delete audit logs older than 7 days"

    def handle(self, *args, **options):
        cutoff_date = timezone.now() - timedelta(days=7)

        old_logs = AuditLog.objects.filter(
            timestamp__lt=cutoff_date
        )

        count = old_logs.count()

        old_logs.delete()

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully deleted {count} old audit logs."
            )
        )