from django.core.management.base import BaseCommand
from core.faker import generate

class Command(BaseCommand):
    help = "Seed DB with fake data"

    def handle(self, *args, **kwargs):
        generate()
        self.stdout.write(self.style.SUCCESS("Seed done"))
