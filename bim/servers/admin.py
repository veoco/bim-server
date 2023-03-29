from django.contrib import admin

from .models import Machine, Server, Task


class MachineAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "ip", "token", "status")


class ServerAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "token",
        "download_url",
        "upload_url",
        "ipv6",
        "multi",
    )


class TaskAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "machine",
        "server",
        "upload",
        "upload_status",
        "download",
        "download_status",
        "latency",
        "jitter",
        "status",
    )


admin.site.register(Machine, MachineAdmin)
admin.site.register(Server, ServerAdmin)
admin.site.register(Task, TaskAdmin)
