from datetime import timedelta, datetime
from collections import defaultdict

from django.conf import settings
from django.utils import timezone

from ninja import Router
from ninja.security import APIKeyHeader
from ninja.errors import HttpError

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

router = Router()


class ApiKey(APIKeyHeader):
    param_name = "X-API-Key"

    def authenticate(self, request, key):
        if key == settings.API_KEY:
            return True
        raise HttpError(401, "Invalid token")


@router.post("/machines/", auth=ApiKey(), response={201: MachineItem})
def create_machine(request, form: MachineCreate):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")

    name = form.name
    machine = Machine.objects.filter(name=name).first()
    if machine:
        machine.ip = ip
        machine.save()
    else:
        machine = Machine.objects.create(ip=ip, name=name)
    return 201, machine


@router.get("/machines/latest", response=list[MachineItem])
def list_machines(request):
    return Machine.objects.order_by("-pk")[:20]


@router.get("/machines/{mid}/", response={200: MachineWithTargets, 404: Message})
def get_machine(request, mid: int):
    if not Machine.objects.filter(pk=mid).exists():
        return 404, {"msg": "Not found"}

    machine = Machine.objects.get(pk=mid)
    targets = list(Target.objects.all())
    return {"detail": machine, "targets": targets}


@router.get(
    "/targets/worker",
    auth=ApiKey(),
    response=list[TargetWorkerItem],
)
def list_targets(request):
    return Target.objects.all().order_by("-pk")[:20]


@router.post("/machines/{mid}/targets/{tid}/", auth=ApiKey(), response=Message)
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


@router.get(
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
    data = TcpPing.objects.filter(
        machine__id=mid, target__id=tid, created__gte=start_time
    )

    if delta == "7d":
        half_hour_groups = defaultdict(
            lambda: {"ping_min": [], "ping_jitter": [], "ping_failed": []}
        )

        for record in data:
            created = record.created
            rounded_time = created.replace(
                minute=(created.minute // 30) * 30, second=0, microsecond=0
            )
            half_hour_groups[rounded_time]["ping_min"].append(record.ping_min)
            half_hour_groups[rounded_time]["ping_jitter"].append(record.ping_jitter)
            half_hour_groups[rounded_time]["ping_failed"].append(record.ping_failed)

        ping_data_list = []

        for half_hour, values in sorted(half_hour_groups.items()):
            ping_data = TcpPingData(
                created=half_hour,
                ping_min=(
                    sum(values["ping_min"]) / len(values["ping_min"])
                    if values["ping_min"]
                    else 0
                ),
                ping_jitter=(
                    sum(values["ping_jitter"]) / len(values["ping_jitter"])
                    if values["ping_jitter"]
                    else 0
                ),
                ping_failed=(
                    sum(values["ping_failed"]) // len(values["ping_failed"])
                    if values["ping_failed"]
                    else 0
                ),
            )
            ping_data_list.append(ping_data)

        return ping_data_list

    return data
