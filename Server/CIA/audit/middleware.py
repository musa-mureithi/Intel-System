import json
from .models import AuditLog
from .security import limit_audit_data


class AuditMiddleware:

    EXCLUDED_PATHS = {
       # "/api/audit/get_logs/",
        #"/get_logs/",
    }

    # Do not capture bodies from authentication endpoints
    SENSITIVE_PATHS = (
        "/login/",
        "/register/",
        "/password-reset/",
        "/change-password/",
        "/token/",
        "/unified_search/",
    )

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        try:
            if request.path in self.EXCLUDED_PATHS:
                return response

            sensitive_endpoint = any(
                path in request.path.lower()
                for path in self.SENSITIVE_PATHS
            )

            request_data = None
            response_data = None

            if not sensitive_endpoint:
                request_data = limit_audit_data(
                    self.get_body(request),
                    max_chars=2000
                )

                response_data = limit_audit_data(
                    self.get_response_data(response),
                    max_chars=3000
                )

            AuditLog.objects.create(
                user=(
                    request.user
                    if request.user.is_authenticated
                    else None
                ),
                action_type="API_CALL",
                description=f"{request.method} {request.path}",
                resource=request.path,
                endpoint=request.path,
                request_method=request.method,
                status_code=response.status_code,
                ip_address=self.get_ip(request),
                user_agent=request.META.get("HTTP_USER_AGENT"),
                request_data=request_data,
                response_data=response_data,
            )

        except Exception as e:
            print("Audit error:", e)

        return response

    def get_ip(self, request):
        return request.META.get("REMOTE_ADDR")

    def get_body(self, request):
        try:
            if hasattr(request, "data"):
                return request.data

            return json.loads(request.body.decode("utf-8"))

        except (ValueError, UnicodeDecodeError, AttributeError):
         return None

        except Exception as e:
            print("Request body audit error:", e)
        return None

    def get_response_data(self, response):
        try:
            content_type = response.get("Content-Type", "")

            if "application/json" not in content_type:
                return None

            return json.loads(response.content.decode())

        except (ValueError, UnicodeDecodeError, AttributeError):
            return None