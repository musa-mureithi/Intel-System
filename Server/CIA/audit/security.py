import json

SENSITIVE_FIELDS = {
    "password",
    "old_password",
    "new_password",
    "confirm_password",
    "token",
    "access",
    "refresh",
    "access_token",
    "refresh_token",
    "authorization",
    "secret",
    "client_secret",
    "api_key",
    "private_key",
    "otp",
    "otp_code",
    "verification_code",
    "cookie",
    "sessionid",
    "author",
    "content",
    "totp_secret",
    "image"
}


def sanitize_audit_data(data):
    if isinstance(data, dict):
        cleaned = {}

        for key, value in data.items():
            if key.lower() in SENSITIVE_FIELDS:
                cleaned[key] = "[REDACTED]"
            else:
                cleaned[key] = sanitize_audit_data(value)

        return cleaned

    if isinstance(data, list):
        return [sanitize_audit_data(item) for item in data]

    return data


def limit_audit_data(data, max_chars=3000):
    if data is None:
        return None

    data = sanitize_audit_data(data)
    serialized = json.dumps(data, default=str)

    if len(serialized) > max_chars:
        return {
            "truncated": True,
            "preview": serialized[:max_chars]
        }

    return data

def detect_failed_logins():
    """
    Placeholder for failed-login detection.

    Implement the actual signal receiver once the login
    signal and authentication flow are confirmed.
    """
    pass
