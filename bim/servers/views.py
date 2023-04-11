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
    MachineWithTargets,
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
    return Machine.objects.order_by("-pk")[:20]


@api.post("/machines/{mid}/", response={200: MachineWithTargets, 404: Message})
def get_machine(request, mid: int):
    if not Machine.objects.filter(pk=mid).exists():
        return 404, {"msg": "Not found"}

    machine = Machine.objects.get(pk=mid)
    targets = list(Target.objects.all())
    return {"detail": machine, "targets": targets}


@api.post(
    "/targets/worker",
    auth=ApiKey(),
    response=list[TargetWorkerItem],
)
def list_targets(request):
    return Target.objects.all().order_by("-pk")[:20]


@api.post("/machines/{mid}/targets/{tid}/", auth=ApiKey(), response=Message)
def add_tcp_ping_data(request, mid: int, tid: int, form: TcpPingCreate):
    if (not Machine.objects.filter(pk=mid).exists()) or (
        not Target.objects.filter(pk=tid).exists()
    ):
        return 404, {"msg": "Not found"}

    target = Target.objects.get(pk=tid)
    machine = Machine.objects.get(pk=mid)
    TcpPing.objects.create(
        machine=machine,
        target=target,
        ping_min=form.ping_min,
        ping_jitter=form.ping_jitter,
        ping_failed=form.ping_failed,
    )

    return 200, {"msg": "ok"}


@api.post(
    "/machines/{mid}/targets/{tid}/{delta}",
    response={200: list[TcpPingData], 404: Message},
)
def list_tcp_ping_data(request, mid: int, tid: int, delta: str):
    if (not Machine.objects.filter(pk=mid).exists()) or (
        not Target.objects.filter(pk=tid).exists()
    ):
        return 404, {"msg": "Not found"}

    if delta == "latest":
        t = timedelta(hours=24)
    elif delta == "7d":
        t = timedelta(days=7)
    else:
        return 404, {"msg": "Not found"}

    start_time = timezone.now() - t
    return TcpPing.objects.filter(
        machine__id=mid, target__id=tid, created__gte=start_time
    )
