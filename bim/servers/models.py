from django.db import models


class Machine(models.Model):
    name = models.CharField(max_length=32)
    ip = models.GenericIPAddressField(db_index=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Target(models.Model):
    machine = models.ForeignKey(
        Machine,
        on_delete=models.CASCADE,
        related_name="targets",
        related_query_name="target",
    )
    name = models.CharField(max_length=32)
    url = models.URLField(db_index=True)
    ipv6 = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class TcpPing(models.Model):
    target = models.ForeignKey(
        Target,
        on_delete=models.CASCADE,
        related_name="tcp_pings",
        related_query_name="tcp_ping",
    )
    created = models.DateTimeField(auto_now_add=True)

    ping_min = models.FloatField(null=True, blank=True)
    ping_jitter = models.FloatField(null=True, blank=True)
    ping_failed = models.SmallIntegerField(default=0)
