from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from rounds.models import TcpPing, Machine


class Command(BaseCommand):
    help = "Check Machine and Task status"

    def handle(self, *args, **options):
        due_time = timezone.now() - timedelta(days=7)

        tcpping_count, _ = TcpPing.objects.filter(created__lte=due_time).delete()

        machine_count = 0
        for machine in Machine.objects.filter(created__lte=due_time):
            if TcpPing.objects.filter(machine=machine).count() == 0:
                machine.delete()
                machine_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully cleaned {machine_count} machine, {tcpping_count} tcping data"
            )
        )
