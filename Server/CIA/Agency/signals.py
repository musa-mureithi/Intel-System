from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Person
from .services.faiss_service import build_index


@receiver(post_save, sender=Person)
def update_faiss_on_save(sender, instance, **kwargs):
    try:
        build_index()  # rebuild FAISS
    except Exception as e:
        print(f"Error rebuilding FAISS index: {e}")


@receiver(post_delete, sender=Person)
def update_faiss_on_delete(sender, instance, **kwargs):
    try:
        build_index()
    except Exception as e:
        print(f"Error rebuilding FAISS index: {e}")