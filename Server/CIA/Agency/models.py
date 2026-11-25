from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from .utils.encryption import EncryptedCharField, EncryptedTextField
import uuid


class Person(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    totp_secret = models.CharField(max_length=50, blank=True, null=True)
    PERSON_TYPE_CHOICES =[
      ('DIRECTOR', 'DIRECTOR'),
      ('VCE-DIRECTOR', 'VCE-DIRECTOR'),
      ('COMMANDER', 'COMMANDER'),
      ('INTELLIGENCE-ANALYST', 'INTELLIGENCE-ANALYST'),
      ('FIELD-AGENT', 'FIELD-AGENT'),
      ('SOLDIER', 'SOLDIER'),
      ('INFORMANT', 'INFORMANT'),
      ('CIVILIAN', 'CIVILIAN'),
      ]

    full_name = models.CharField(max_length=100)
    person_type = models.CharField(max_length=100, choices=PERSON_TYPE_CHOICES)

    UNIT_TYPE_CHOICES = [
        ('HQ', 'HQ'),
        ('INTELLIGENCE', 'INTELLIGENCE'),
        ('OPERATIONS', 'OPERATIONS'),
        ('SUPPORT', 'SUPPORT'),

    ]
    unit_type = models.CharField(max_length=100, choices=UNIT_TYPE_CHOICES, null=True, blank=True)

    CLEARANCE_TYPE_CHOICES = [
        ('Top-secret', 'TOP-SECRET'),
        ('SECRET', 'SECRET'),
        ('CLASSIFIED', 'CLASSIFIED'),
        ('CONFIDENTIAL', 'CONFIDENTIAL'),
        ('UNCLASSIFIED', 'UNCLASSIFIED'),
    

    ]
    clearance_type = models.CharField(max_length=100, choices=CLEARANCE_TYPE_CHOICES, null=True, blank=True)
    CLEARANCE_LEVEL_CHOICES = [
    (6, 'ADMIN'),
    (5, 'HIGH COMMAND'),
    (4, 'COMMAND'),
    (3, 'OPERATIONAL'),
    (1, 'LOW'),
]
    clearance_level = models.IntegerField(
    choices=CLEARANCE_LEVEL_CHOICES,
    null=True,
    blank=True
)
    blood_type = EncryptedCharField()
   
    id_dna = EncryptedCharField(blank=True)

    def save(self, *args, **kwargs):
        if not self.id_dna:
            
            self.id_dna = str(uuid.uuid4())
        super().save(*args, **kwargs)
    image= models.ImageField(upload_to='person_images/', null=True, blank=True)
    status = models.CharField(max_length=100, default='ACTIVE')
    face_embeddings = EncryptedTextField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    identity_number = models.CharField(max_length=100, unique=True)
   

    def __str__(self):
        return f"{self.full_name} ({self.person_type})"
    

class Operation(models.Model):
    id = models.AutoField(primary_key=True)
    identity_number = models.CharField(max_length=100, unique=True)
    mission_name = EncryptedCharField(max_length=100)
    description = EncryptedTextField()
    
    CLEARANCE_TYPE_CHOICES = [
        ('TOP-SECRET', 'TOP-SECRET'),
        ('SECRET', 'SECRET'),
        ('CLASSIFIED', 'CLASSIFIED'),
        ('CONFIDENTIAL', 'CONFIDENTIAL'),
        ('UNCLASSIFIED', 'UNCLASSIFIED'),

    ]
    clearance_type = models.CharField(max_length=100, choices=CLEARANCE_TYPE_CHOICES)
    external_personnel = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey("person", on_delete=models.SET_NULL, null=True, related_name="created_operations")
    updated_by = models.ForeignKey("person", on_delete=models.SET_NULL, null=True, related_name="updated_operations")
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.mission_name
    

class OperationAssignment(models.Model):
    id = models.BigAutoField(primary_key=True)
    operation = models.ForeignKey(Operation, on_delete=models.CASCADE, related_name="assignments")
    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name="assignments")
    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("operation", "person")  # Prevent duplicate assignments

    def __str__(self):
        return f"{self.person.full_name} → {self.operation.mission_name}"    

class Report(models.Model):
    id = models.AutoField(primary_key=True)
    operation = models.ForeignKey(Operation, on_delete=models.CASCADE, related_name='reports')
    content = EncryptedTextField()
    author = models.ForeignKey(Person, on_delete=models.SET_NULL, null=True, related_name='reports')
    subject = EncryptedCharField(max_length=10000, blank=True)
    role_based_access = models.CharField(
        max_length=1000,
        choices=[
            ('TOP-SECRET', 'TOP-SECRET'),
            ('SECRET', 'SECRET'),
            ('CONFIDENTIAL', 'CONFIDENTIAL'),
            ('UNCLASSIFIED', 'UNCLASSIFIED')
        ],
        default='CONFIDENTIAL'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.subject or f"Report on {self.operation}"
