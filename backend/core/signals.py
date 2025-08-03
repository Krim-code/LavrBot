from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.conf import settings
import os

@receiver(post_migrate)
def load_fake_data(sender, **kwargs):
        from core import faker
        faker.generate()