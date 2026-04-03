from django.contrib import admin
from .models import  Person, OperationAssignment, Operation, Report
from  deepface import DeepFace
import tempfile

@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'person_type', 'identity_number')
    list_filter = ('person_type', 'unit_type', 'clearance_type', 'status')
    search_fields = ('full_name', 'id_dna', 'identity_number')

    def save_model(self, request, obj, form, change):
        if obj.image:
            obj.image.seek(0)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_file:
                for chunk in obj.image.chunks():
                    temp_file.write(chunk)
                temp_file.flush()

                result = DeepFace.represent(
                    img_path=temp_file.name,
                    model_name='Facenet',
                    enforce_detection=True
                )

            obj.face_embeddings = str(result[0]['embedding'])
            obj.image.seek(0)
        super().save_model(request, obj, form, change)



admin.site.register(OperationAssignment)
admin.site.register(Operation)
admin.site.register(Report)

