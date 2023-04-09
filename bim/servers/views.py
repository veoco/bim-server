from datetime import timedelta

from django.conf import settings
from django.utils import timezone

from ninja import NinjaAPI
from ninja.security import APIKeyHeader

from .schemas import (
    Message,
    MachineCreate,
    MachineItem,
    TargetWorkerItem,
    TargetItem,
    TcpPingCreate,
    TcpPingData,
)
from .models import Machine, Target, TcpPing

api = NinjaAPI()


class InvalidToken(Exception):
    pass


@api.exception_handler(InvalidToken)
def on_invalid_token(request, exc):
    return api.create_response(request, {"msg": "Invalid token"}, status=401)


class ApiKey(APIKeyHeader):
    param_name = "X-API-Key"

    def authenticate(self, request, key):
        if key == settings.API_KEY:
            return True
        raise InvalidToken


@api.post("/machines/", auth=ApiKey(), response={201: MachineItem})
def create_machine(request, form: MachineCreate):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")

    name = form.name

    if Machine.objects.filter(ip=ip, name=name).exists():
        machine = Machine.objects.get(ip=ip, name=name)
        machine.save()
    else:
        machine = Machine.objects.create(ip=ip, name=name)
    return 201, machine


@api.post("/machines/latest", response=list[MachineItem])
def list_machines(request):
    return Machine.objects.order_by("-status", "-pk")[:20]


@api.post(
    "/machines/{mid}/targets/worker", auth=ApiKey(), response={200: list[TargetWorkerItem], 404: Message}
)
def list_worker_target(request, mid: int):
    if not Machine.objects.filter(pk=mid).exists():
        return 404, {"msg": "Not found"}

    return Target.objects.filter(machine__id=mid).order_by("-pk")[:20]


@api.post(
    "/machines/{mid}/targets/", response={200: list[TargetItem], 404: Message}
)
def list_target(request, mid: int):
    if not Machine.objects.filter(pk=mid).exists():
        return 404, {"msg": "Not found"}

    return Target.objects.filter(machine__id=mid).order_by("-pk")[:20]


@api.post("/machines/{mid}/targets/{tid}/", auth=ApiKey(), response=Message)
def add_tcp_ping_data(request, mid: int, tid: int, form: TcpPingCreate):
    if (
        not Target.objects.select_related("machine")
        .filter(tid=tid, machine__id=mid)
        .exists()
    ):
        return 404, {"msg": "Not found"}

    target = Target.objects.get(pk=tid)
    TcpPing.objects.create(
        target=target,
        ping_min=form.ping_min,
        ping_jitter=form.ping_jitter,
        ping_failed=form.ping_failed,
    )

    return 200, {"msg": "ok"}


@api.post(
    "/machines/{mid}/targets/{tid}/latest",
    response={200: list[TcpPingData], 404: Message},
)
def list_tcp_ping_data(request, mid: int, tid: int):
    if (
        not Target.objects.select_related("machine")
        .filter(tid=tid, machine__id=mid)
        .exists()
    ):
        return 404, {"msg": "Not found"}

    start_time = timezone.now() - timedelta(hours=25)
    return TcpPing.objects.filter(modified__gte=start_time)
