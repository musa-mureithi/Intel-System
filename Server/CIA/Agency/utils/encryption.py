from cryptography.fernet import Fernet
from django.conf import settings
from django.db import models

cipher = Fernet(settings.ENCRYPTION_KEY)


# 🔐 Helper functions
def encrypt_data(data: str) -> str:
    if data is None:
        return None
    try:
        return cipher.encrypt(data.encode()).decode()
    except Exception:
        return data

def decrypt_data(data: str) -> str:
    if data is None:
        return None
    try:
        return cipher.decrypt(data.encode()).decode()
    except Exception:
        return data


# 🔐 Custom Django Fields
class EncryptedCharField(models.CharField):

    def get_prep_value(self, value):
        return encrypt_data(value)

    def from_db_value(self, value, expression, connection):
        return decrypt_data(value)

    def to_python(self, value):
        return decrypt_data(value)


class EncryptedTextField(models.TextField):

    def get_prep_value(self, value):
        return encrypt_data(value)

    def from_db_value(self, value, expression, connection):
        return decrypt_data(value)

    def to_python(self, value):
        return decrypt_data(value)