from django.contrib import admin

from .models import Machine, Target, TcpPing


class MachineAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "ip", "created")


class TargetAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "machine",
        "name",
        "url",
        "ipv6",
        "created",
    )


class TcpPingAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "target",
        "ping_min",
        "ping_jitter",
        "created",
    )


admin.site.register(Machine, MachineAdmin)
admin.site.register(Target, TargetAdmin)
admin.site.register(TcpPing, TcpPingAdmin)
