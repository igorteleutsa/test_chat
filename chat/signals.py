from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from .models import Thread


@receiver(m2m_changed, sender=Thread.participants.through)
def validate_participants(sender, instance, action, **kwargs):
    if action == 'pre_add':
        if instance.participants.count() + len(kwargs.get('pk_set', [])) > 2:
            raise ValueError("A thread can't have more than 2 participants.")
