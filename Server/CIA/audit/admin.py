from django.contrib import admin
from .models import AuditLog

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "action_type",
        "resource",
        "resource_id",
        "ip_address",
        "timestamp",
    )
    list_filter = ("action_type", "resource", "timestamp")
    search_fields = ("user__username", "resource", "description", "ip_address")

    readonly_fields = (
        "user",
        "action_type",
        "description",
        "resource",
        "resource_id",
        "ip_address",
        "user_agent",
        "request_method",
        "endpoint",
        "status_code",
        "request_data",
        "response_data",
        "old_data",
        "new_data",
        "timestamp",
    )


    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


    def has_view_permission(self, request, obj=None):
        return request.user.is_superuser

   
    ordering = ("-timestamp",)
    list_per_page = 50