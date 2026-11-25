from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class AuditLog(models.Model):
    id = models.AutoField(primary_key=True)
    ACTION_TYPES = [
        ("LOGIN", "Login"),
        ("LOGOUT", "Logout"),
        ("FAILED_LOGIN", "Failed Login"),
        ("VIEW", "View"),
        ("PAGE", "Page Visit"),
        ("CREATE", "Create"),
        ("UPDATE", "Update"),
        ("DELETE", "Delete"),
        ("SEARCH", "Search"),
        ("EXPORT", "Export"),
        ("API_CALL", "API Call"),
    ]

    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)

    action_type = models.CharField(max_length=20, choices=ACTION_TYPES)
    description = models.TextField()

    resource = models.CharField(max_length=255, null=True, blank=True)
    resource_id = models.CharField(max_length=100, null=True, blank=True)

    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)

    request_method = models.CharField(max_length=10, null=True, blank=True)
    endpoint = models.CharField(max_length=255, null=True, blank=True)
    status_code = models.IntegerField(null=True, blank=True)

    request_data = models.JSONField(null=True, blank=True)
    response_data = models.JSONField(null=True, blank=True)

    old_data = models.JSONField(null=True, blank=True)
    new_data = models.JSONField(null=True, blank=True)

    timestamp = models.DateTimeField(auto_now_add=True)

    def delete(self, *args, **kwargs):
        raise Exception("Audit logs cannot be deleted")
    
    class Meta:
        ordering = ["-timestamp"]
        

     