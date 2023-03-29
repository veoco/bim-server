from ninja import NinjaAPI

from .schemas import *
from .models import *

api = NinjaAPI()


@api.post("/machines/", response={201: MachineItem})
def create_machine(request, form: MachineCreate):
    token = form.token

    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")

    if Machine.objects.filter(token=token, ip=ip).exists():
        machine = Machine.objects.get(token=token, ip=ip)
        machine.status = 1  # 1: Online
        machine.save()
    else:
        name = form.name
        machine = Machine.objects.create(ip=ip, name=name, token=token)
    return 201, machine


@api.get("/machines/", response=list[MachineItem])
def list_machines(request, token: str):
    return Machine.objects.filter(token=token).order_by("-pk")[:20]


@api.post("/servers/", response={201: ServerItem})
def create_server(request, form: ServerCreate):
    server = Server.objects.create(
        token=form.token,
        name=form.name,
        download_url=str(form.download_url),
        upload_url=str(form.upload_url),
        ipv6=form.ipv6,
        multi=form.multi,
    )

    token = form.token
    online_machines = Machine.objects.filter(token=token).exclude(
        status=0  # 0: Offline
    )[:20]
    for i, machine in enumerate(online_machines):
        status = 1 if i != 0 else 2  # 1: Block, 2: Work
        Task.objects.create(
            server=server,
            machine=machine,
            status=status,
        )

    return 201, server


@api.get("/servers/", response=list[ServerItem])
def list_servers(request, token: str):
    return Server.objects.filter(token=token).order_by("-pk")[:20]


@api.post("/tasks/{pk}", response=Message)
def finish_task(request, pk: int, token: str, form: TaskFinish):
    if (
        not Task.objects.select_related("machine")
        .filter(pk=pk, machine__token=token, status=2)  # 2: Work
        .exists()
    ):
        return 404, {"msg": "Not found"}

    task = Task.objects.get(pk=pk)

    task.download = form.download
    task.download_status = form.download_status
    task.upload = form.upload
    task.upload_status = form.upload_status
    task.latency = form.latency
    task.jitter = task.jitter
    task.status = 3  # Finish
    task.save()

    for t in Task.objects.filter(server=task.server, status=1):  # 1: Block
        t.status = 2  # 2: Work
        t.save()
        break

    return 200, {"msg": "ok"}


@api.get("/tasks/", response=list[TaskWithMachineAndServerItem])
def list_tasks(
    request,
    token: str,
    machine_id: int = None,
    server_id: int = None,
    status: int = None,
):
    if Machine.objects.filter(pk=machine_id).exists():
        machine = Machine.objects.get(pk=machine_id)
        machine.save()

    tasks = (
        Task.objects.select_related("machine", "server")
        .filter(machine__token=token)
        .filter(server__token=token)
    )
    if machine_id:
        tasks = tasks.filter(machine_id=machine_id)
    if server_id:
        tasks = tasks.filter(server_id=server_id)
    if status:
        tasks = tasks.filter(status=status)

    return tasks
