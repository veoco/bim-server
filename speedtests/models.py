from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model


class User(AbstractUser):
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    username = models.CharField(max_length=32, unique=True)
    email = models.EmailField(max_length=32, unique=True)
    token = models.CharField(max_length=32)


class ServerList(models.Model):
    name = models.CharField(max_length=64)
    readme = models.TextField(max_length=2000, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name="server_lists",
        related_query_name="server_list",
        blank=True,
        null=True,
    )
    detail = models.JSONField(blank=True, null=True)


class Server(models.Model):
    class Provider(models.TextChoices):
        OOKLA = "Ookla", "Ookla"
        LIBRESPEED = "LibreSpeed", "LibreSpeed"

    provider = models.CharField(
        max_length=32,
        choices=Provider.choices,
        default=Provider.OOKLA,
    )
    owner = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name="servers",
        related_query_name="server",
        blank=True,
        null=True,
    )
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    detail = models.JSONField()


class Machine(models.Model):
    id = models.UUIDField(primary_key=True)
    owner = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name="server_results",
        related_query_name="server_result",
    )
    ip = models.GenericIPAddressField()
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField()


class MachineTask(models.Model):
    class State(models.TextChoices):
        WAIT = "Wait", "Wait"
        WORK = "Work", "Work"
        FINISH = "Finish", "Finish"

    machine = models.ForeignKey(
        "Machine",
        on_delete=models.CASCADE,
        related_name="tasks",
        related_query_name="task",
    )
    state = models.CharField(
        max_length=32,
        choices=State.choices,
        default=State.WAIT,
    )
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    oneshot = models.BooleanField()
    detail = models.JSONField()
