from django.db import models


class Machine(models.Model):
    token = models.SlugField(max_length=64, db_index=True)
    name = models.CharField(max_length=16)
    ip = models.GenericIPAddressField(db_index=True)

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    status = models.SmallIntegerField(default=1)


class Server(models.Model):
    token = models.SlugField(max_length=64, db_index=True)
    name = models.CharField(max_length=16)

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    download_url = models.URLField()
    upload_url = models.URLField()
    ipv6 = models.BooleanField(default=False)
    multi = models.BooleanField(default=False)


class Task(models.Model):
    machine = models.ForeignKey(
        Machine,
        on_delete=models.CASCADE,
        related_name="tasks",
        related_query_name="task",
        db_constraint=False
    )
    server = models.ForeignKey(
        Server,
        on_delete=models.CASCADE,
        related_name="tasks",
        related_query_name="task",
        db_constraint=False
    )

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    status = models.SmallIntegerField(default=1)

    download = models.FloatField(default=0)
    download_status = models.CharField(max_length=16, default="")
    upload = models.FloatField(default=0)
    upload_status = models.CharField(max_length=16, default="")
    latency = models.FloatField(default=0)
    jitter = models.FloatField(default=0)
