from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from servers.models import Machine, Task


class Command(BaseCommand):
    help = "Check Machine and Task status"

    def handle(self, *args, **options):
        due_time = timezone.now() - timedelta(minutes=1)

        Machine.objects.filter(modified__lte=due_time, status=1).update(status=0)
        Task.objects.filter(modified__lte=due_time, status=2).update(status=4)

        self.stdout.write(self.style.SUCCESS("Successfully checked"))
