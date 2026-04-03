import json
from .models import AuditLog

class AuditMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        try:
            AuditLog.objects.create(
                user=request.user if request.user.is_authenticated else None,
                action_type="API_CALL",
                description=f"{request.method} {request.path}",
                resource=request.path,
                endpoint=request.path,
                request_method=request.method,
                status_code=response.status_code,
                ip_address=self.get_ip(request),
                user_agent=request.META.get("HTTP_USER_AGENT"),
                request_data=self.get_body(request),
                response_data=self.get_response_data(response),
            )
        except Exception as e:
            print("Audit error:", e)

        return response

    def get_ip(self, request):
        return request.META.get("REMOTE_ADDR")

    def get_body(self, request):
        try:
            return json.loads(request.body.decode())
        except:
            return None

    def get_response_data(self, response):
        try:
            return json.loads(response.content.decode())
        except:
            return None