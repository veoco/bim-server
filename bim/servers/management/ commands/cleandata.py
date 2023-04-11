from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from servers.models import TcpPing


class Command(BaseCommand):
    help = "Check Machine and Task status"

    def handle(self, *args, **options):
        due_time = timezone.now() - timedelta(days=7)

        count, _ = TcpPing.objects.filter(created__lte=due_time).delete()

        self.stdout.write(self.style.SUCCESS(f"Successfully cleaned {count} data"))