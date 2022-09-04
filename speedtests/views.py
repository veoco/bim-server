from django.http import JsonResponse
from django.core.exceptions import ValidationError
from django.views import View
from django.db.models import Q, When, Case
from django.utils import timezone
from django.core.validators import URLValidator
from asgiref.sync import sync_to_async
from paka import cmark

from .models import Server, ServerList, Machine, MachineTask
from .utils import (
    aget_object_or_none,
    get_json_or_none,
    aget_request_user_or_none,
    aclean_then_save_instance,
    aget_fk,
    aget_user_and_data,
    create_user,
    authenticate_user,
    user_login,
    user_logout,
    create_rrd,
    update_rrd,
    fetch_rrd,
)


class SearchAPIView(View):
    async def query_server(self, query):
        res = {"count": 0, "results": []}
        if query.isdigit():
            servers = Server.objects.filter(Q(id=query))
        elif query.isalpha() and query.isupper() and len(query) == 2:
            servers = Server.objects.filter(Q(detail__cc=query))
        else:
            servers = Server.objects.filter(
                Q(provider__icontains=query)
                | Q(detail__sponsor__icontains=query)
                | Q(detail__name__icontains=query)
                | Q(detail__sponsorName__icontains=query)
            )
        async for server in servers.select_related("owner")[:100]:
            owner = server.owner
            res["count"] += 1
            res["results"].append(
                {
                    "pk": server.pk,
                    "provider": server.provider,
                    "owner": {"pk": owner.pk, "username": owner.username}
                    if owner
                    else None,
                    "detail": server.detail,
                }
            )
        return res

    async def query_server_list(self, query):
        res = {"count": 0, "results": []}
        if query.isdigit():
            server_lists = ServerList.objects.filter(id=query)
        else:
            server_lists = ServerList.objects.filter(
                Q(name__icontains=query) | Q(readme__icontains=query)
            )
        async for server_list in server_lists.select_related("owner")[:100]:
            owner = server_list.owner
            readme = server_list.readme.split("\n")[0] if server_list.readme else ""

            res["count"] += 1
            res["results"].append(
                {
                    "pk": server_list.pk,
                    "name": server_list.name,
                    "readme": cmark.to_html(readme),
                    "created": server_list.created,
                    "modified": server_list.modified,
                    "owner": {"pk": owner.pk, "username": owner.username}
                    if owner
                    else None,
                }
            )
        return res

    async def get(self, request, *args, **kwargs):
        query_type = request.GET.get("type")
        query = request.GET.get("query")

        if query_type == "server":
            res = await self.query_server(query)
        elif query_type == "server_list":
            res = await self.query_server_list(query)
        else:
            res = {"count": 0, "results": []}
        return JsonResponse(res)


class ServerAPIView(View):
    async def get(self, request, *args, **kwargs):
        server_id = request.GET.get("pk")

        if server_id:
            server = await aget_object_or_none(Server, pk=server_id)
            if server:
                owner = await aget_fk(server, "owner")
                res = {
                    "pk": server.pk,
                    "provider": server.provider,
                    "created": server.created,
                    "modified": server.modified,
                    "owner": {"pk": owner.pk, "username": owner.username}
                    if owner
                    else None,
                    "detail": server.detail,
                }

                user = await aget_request_user_or_none(request)
                if user and (owner == user or user.is_superuser):
                    res.update({"editable": True})

                return JsonResponse(res)

        res = JsonResponse({"msg": "Not found"})
        res.status_code = 404
        return res

    async def post(self, request, *args, **kwargs):
        try:
            user, data = await aget_user_and_data(request)

            pk = data.get("pk")
            ipv6 = data.get("ipv6")
            dl = data.get("dl")
            ul = data.get("ul")
            sponsor_name = data.get("sponsor_name")
            name = data.get("name")

            provider = Server.Provider.LIBRESPEED

            exist = False
            if pk:
                exist = await Server.objects.filter(pk=pk).aexists()

            ipv6 = True if ipv6 else False

            v = URLValidator()
            v(dl)
            v(ul)

            if not sponsor_name:
                raise ValidationError({"sponsor_name": "Invalid"})

            if not name:
                raise ValidationError({"name": "Invalid"})

            if exist:
                server = await Server.objects.select_related("owner").aget(pk=pk)
                if server.owner != user and not user.is_superuser:
                    raise ValidationError({"user": "Permission deny"})
            else:
                server = Server(provider=provider, owner=user, detail={})

            server.detail.update(
                {
                    "name": name,
                    "sponsorName": sponsor_name,
                    "ipv6": ipv6,
                    "dl": dl,
                    "ul": ul,
                    "id": 0,
                }
            )
            await aclean_then_save_instance(server)

            return JsonResponse({"pk": server.pk})
        except ValidationError as e:
            if not hasattr(e, "error_dict"):
                res = JsonResponse({"msg": {"dl": "Invalid"}})
            else:
                res = JsonResponse({"msg": e.message_dict})
            res.status_code = 400
            return res


class ServerListAPIView(View):
    async def get(self, request, *args, **kwargs):
        server_list_id = request.GET.get("pk")
        server_list_edit = request.GET.get("edit")

        try:
            if not server_list_id:
                raise ValidationError({"pk": "Invalid"})
            server_list = await aget_object_or_none(ServerList, pk=server_list_id)
            if not server_list:
                raise ValidationError({"pk": "Invalid"})

            server_ids = server_list.detail.get("server_ids", [])
            res = {
                "pk": server_list.pk,
                "name": server_list.name,
                "readme": server_list.readme,
                "server_ids": server_ids,
            }

            servers = []
            preserved = Case(
                *[When(id=cid, then=pos) for pos, cid in enumerate(server_ids)]
            )
            async for server in Server.objects.filter(id__in=server_ids).order_by(
                preserved
            ):
                s = {
                    "pk": server.pk,
                    "provider": server.provider,
                    "detail": server.detail,
                }
                servers.append(s)
            res.update({"servers": servers})

            if not server_list_edit:
                owner = await aget_fk(server_list, "owner")
                user = await aget_request_user_or_none(request)
                res.update(
                    {
                        "readme": cmark.to_html(server_list.readme),
                        "created": server_list.created,
                        "modified": server_list.modified,
                        "owner": {"pk": owner.pk, "username": owner.username}
                        if owner
                        else None,
                    }
                )
                if user and (owner == user or user.is_superuser):
                    res.update({"editable": True})
            return JsonResponse(res)
        except ValidationError as e:
            res = JsonResponse({"msg": e.message_dict})
            res.status_code = 404
            return res

    async def post(self, request, *args, **kwargs):
        try:
            user, data = await aget_user_and_data(request)

            pk = data.get("pk")
            name = data.get("name")
            readme = data.get("readme")
            server_ids = data.get("servers")

            if server_ids:
                for server_id in server_ids:
                    if not (isinstance(server_id, int) or server_id.isdigit()):
                        raise ValidationError({"servers": "Server ids not found"})

                servers = Server.objects.filter(pk__in=server_ids)
                if await servers.acount() != len(server_ids):
                    raise ValidationError({"servers": "Server ids not found"})

            exist = False
            if pk:
                exist = await ServerList.objects.filter(pk=pk).aexists()

            if exist:
                server_list = await ServerList.objects.select_related("owner").aget(
                    pk=pk
                )
                if server_list.owner != user and not user.is_superuser:
                    raise ValidationError({"user": "Permission deny"})
            else:
                server_list = ServerList(owner=user, detail={})

            server_list.name = name
            server_list.readme = readme
            server_list.detail.update({"server_ids": server_ids})
            await aclean_then_save_instance(server_list)

            return JsonResponse({"pk": server_list.pk})
        except ValidationError as e:
            res = JsonResponse({"msg": e.message_dict})
            res.status_code = 400
            return res


class SignUpView(View):
    async def post(self, request, *args, **kwargs):
        try:
            data = get_json_or_none(request)
            if not data:
                raise ValidationError({"fields": "Empty fields"})

            username = data.get("username")
            email = data.get("email")
            password = data.get("password")

            await sync_to_async(create_user)(username, email, password)
            return JsonResponse({"msg": "ok"})
        except ValidationError as e:
            res = JsonResponse({"msg": e.message_dict})
            res.status_code = 400
            return res


class LoginView(View):
    async def post(self, request, *args, **kwargs):
        try:
            data = get_json_or_none(request)
            if not data:
                raise ValidationError({"fields": "Empty fields"})
            email = data.get("email", None)
            password = data.get("password", None)

            user = await sync_to_async(authenticate_user)(request, email, password)
            if user is None:
                raise ValidationError({"fields": "Username or Password error"})

            await sync_to_async(user_login)(request, user)
            return JsonResponse({"msg": "ok"})
        except ValidationError as e:
            res = JsonResponse({"msg": e.message_dict})
            res.status_code = 400
            return res


class LogoutView(View):
    async def post(self, request, *args, **kwargs):
        user = await aget_request_user_or_none(request)
        if user:
            await sync_to_async(user_logout)(request)
            return JsonResponse({"msg": "ok"})
        else:
            res = JsonResponse({"msg": "You are not logined"})
            res.status_code = 400
            return res


class MyView(View):
    async def get(self, request, *args, **kwargs):
        try:
            user = await aget_request_user_or_none(request)
            if not user:
                raise ValidationError({"user": "Login required"})

            results = {
                "user": {
                    "username": user.username,
                    "email": user.email,
                    "token": user.token,
                }
            }

            mr = {"count": 0, "results": []}
            async for machine in Machine.objects.filter(owner=user):
                task_count = await machine.tasks.filter(
                    Q(state=MachineTask.State.WAIT) | Q(state=MachineTask.State.WORK)
                ).acount()
                mr["results"].append(
                    {
                        "pk": machine.pk,
                        "ip": machine.ip,
                        "task_count": task_count,
                        "created": machine.created,
                        "modified": machine.modified,
                    }
                )
                mr["count"] += 1
            results.update({"machine": mr})

            sr = {"count": 0, "results": []}
            async for server in Server.objects.filter(owner=user):
                sr["results"].append(
                    {
                        "pk": server.pk,
                        "provider": server.provider,
                        "created": server.created,
                        "modified": server.modified,
                        "owner": {"pk": user.pk, "username": user.username},
                        "detail": server.detail,
                    }
                )
                sr["count"] += 1
            results.update({"server": sr})

            slr = {"count": 0, "results": []}
            async for server_list in ServerList.objects.filter(owner=user):
                readme = server_list.readme.split("\n")[0] if server_list.readme else ""
                slr["results"].append(
                    {
                        "pk": server_list.pk,
                        "name": server_list.name,
                        "readme": cmark.to_html(readme),
                        "created": server_list.created,
                        "modified": server_list.modified,
                        "owner": {"pk": user.pk, "username": user.username},
                    }
                )
                slr["count"] += 1
            results.update({"server_list": slr})

            return JsonResponse(results)
        except ValidationError as e:
            res = JsonResponse({"msg": e.message_dict})
            res.status_code = 400
            return res


class MachineView(View):
    async def get(self, request, *args, **kwargs):
        pk = request.GET.get("pk")

        try:
            user = await aget_request_user_or_none(request)
            if not user:
                raise ValidationError({"user": "Login required"})

            machine = await aget_object_or_none(Machine, pk=pk)
            if not machine:
                raise ValidationError({"pk": "Invalid pk"})

            owner = await aget_fk(machine, "owner")
            if owner != user:
                raise ValidationError({"user": "Invalid"})

            task_count = await machine.tasks.filter(
                Q(state=MachineTask.State.WAIT) | Q(state=MachineTask.State.WORK)
            ).acount()
            res = {
                "pk": machine.pk,
                "ip": machine.ip,
                "task_count": task_count,
                "created": machine.created,
                "modified": machine.modified,
                "tasks": [],
            }
            async for machine_task in machine.tasks.all().order_by("-state", "pk"):
                name = f"{machine_task.pk:0>3}"
                filename = f"data/{name[:3]}/{machine_task.pk}.rrd"
                h30 = await sync_to_async(fetch_rrd)(filename, "1h", "end-30h")
                server_id = machine_task.detail.get("server")
                server = await aget_object_or_none(Server, pk=server_id)
                r = {
                    "pk": machine_task.pk,
                    "machine_id": machine.id,
                    "state": machine_task.state,
                    "created": machine_task.created,
                    "modified": machine_task.modified,
                    "oneshot": machine_task.oneshot,
                    "server": {
                        "pk": server.pk,
                        "provider": server.provider,
                        "detail": server.detail,
                    },
                    "detail": machine_task.detail,
                    "30h": h30,
                }
                res["tasks"].append(r)
            return JsonResponse(res)
        except ValidationError as e:
            res = JsonResponse({"msg": e.message_dict})
            res.status_code = 400
            return res

    async def post(self, request, *args, **kwargs):
        try:
            user, data = await aget_user_and_data(request)

            machine_id = data.get("machine_id")
            machine = await aget_object_or_none(Machine, pk=machine_id)

            now = timezone.now()
            ip = request.META.get("HTTP_X_FORWARDED_FOR") or request.META.get(
                "REMOTE_ADDR"
            )
            if machine:
                machine.ip = ip
            else:
                machine = Machine(id=machine_id, owner=user, ip=ip, modified=now)
            await aclean_then_save_instance(machine)

            return JsonResponse({"pk": machine.pk})
        except ValidationError as e:
            res = JsonResponse({"msg": e.message_dict})
            res.status_code = 400
            return res


class MachineTaskView(View):
    async def get(self, request, *args, **kwargs):
        pk = request.GET.get("pk", "")

        try:
            user = await aget_request_user_or_none(request)
            if not user:
                raise ValidationError({"user": "Login required"})

            machine_task = await aget_object_or_none(MachineTask, pk=pk)
            if not machine_task:
                raise ValidationError({"pk": "Invalid pk"})

            machine = await aget_fk(machine_task, "machine")
            owner = await aget_fk(machine, "owner")
            if owner != user:
                raise ValidationError({"user": "Invalid"})

            server_id = machine_task.detail.get("server")
            server = await aget_object_or_none(Server, pk=server_id)
            res = {
                "pk": machine_task.pk,
                "machine_id": machine.id,
                "state": machine_task.state,
                "created": machine_task.created,
                "modified": machine_task.modified,
                "server": {
                    "pk": server.pk,
                    "provider": server.provider,
                    "detail": server.detail,
                },
                "detail": machine_task.detail,
            }
            name = f"{machine_task.pk:0>3}"
            filename = f"data/{name[:3]}/{machine_task.pk}.rrd"
            h30 = await sync_to_async(fetch_rrd)(filename, "1h", "end-30h")
            d10 = await sync_to_async(fetch_rrd)(filename, "1h", "end-10d")
            d360 = await sync_to_async(fetch_rrd)(filename, "1d", "end-360d")
            res.update(
                {
                    "30h": h30,
                    "10d": d10,
                    "360d": d360,
                }
            )
            return JsonResponse(res)
        except ValidationError as e:
            res = JsonResponse({"msg": e.message_dict})
            res.status_code = 404
            return res

    async def post(self, request, *args, **kwargs):
        try:
            user, data = await aget_user_and_data(request)

            machine_id = data.get("machine_id")
            ipv6 = data.get("ipv6")
            thread = data.get("thread")
            server_id = data.get("server_id")

            machine = await aget_object_or_none(Machine, pk=machine_id)
            if not machine:
                raise ValidationError({"machine_id": "Invalid machind id"})

            task_count = await machine.tasks.filter(
                Q(state=MachineTask.State.WAIT) | Q(state=MachineTask.State.WORK)
            ).acount()
            if task_count >= 15:
                raise ValidationError({"machine_id": "Too many tasks"})

            owner = await aget_fk(machine, "owner")
            if user != owner:
                raise ValidationError({"user": "Login required"})

            ipv6 = True if ipv6 else False

            if not isinstance(thread, int) or thread < 1 or thread > 32:
                raise ValidationError({"thead": "Invalid"})

            server = await aget_object_or_none(Server, pk=server_id)
            if not server:
                raise ValidationError({"server_id": "Not found"})

            if ipv6 and not server.detail["ipv6"]:
                raise ValidationError({"ipv6": "Not support"})

            machine_task = MachineTask(
                machine=machine,
                state=MachineTask.State.WAIT,
                oneshot=False,
                detail={"server": server_id, "ipv6": ipv6, "thread": thread},
            )

            await aclean_then_save_instance(machine_task)

            name = f"{machine_task.pk:0>3}"
            filename = f"data/{name[:3]}/{machine_task.pk}.rrd"
            await sync_to_async(create_rrd)(filename)

            return JsonResponse({"pk": machine_task.pk})
        except ValidationError as e:
            res = JsonResponse({"msg": e.message_dict})
            res.status_code = 400
            return res

    async def put(self, request, *args, **kwargs):
        try:
            user, data = await aget_user_and_data(request)

            pk = data.get("pk")

            machine_task = await aget_object_or_none(MachineTask, pk=pk)
            if not machine_task:
                raise ValidationError({"pk": "Invalid"})

            machine = await aget_fk(machine_task, "machine")
            if not machine:
                raise ValidationError({"machine_id": "Invalid machind id"})

            owner = await aget_fk(machine, "owner")
            if user != owner:
                raise ValidationError({"user": "Login required"})

            machine_task.state = MachineTask.State.FINISH

            await aclean_then_save_instance(machine_task)

            return JsonResponse({"msg": "ok"})
        except ValidationError as e:
            res = JsonResponse({"msg": e.message_dict})
            res.status_code = 400
            return res


class MachineTasksView(View):
    async def get(self, request, *args, **kwargs):
        machine_id = request.GET.get("machine_id")

        try:
            user = await aget_request_user_or_none(request)
            if not user:
                raise ValidationError({"user": "Login required"})

            machine = await aget_object_or_none(Machine, pk=machine_id)
            if not machine:
                raise ValidationError({"machine": "Machine ID required"})

            owner = await aget_fk(machine, "owner")
            if user != owner:
                raise ValidationError({"user": "Wrong user"})

            res = {"count": 0, "results": []}
            async for machine_task in machine.tasks.filter(
                Q(state=MachineTask.State.WAIT) | Q(state=MachineTask.State.WORK)
            ):
                server = await aget_object_or_none(
                    Server, pk=machine_task.detail["server"]
                )
                r = {
                    "pk": machine_task.pk,
                    "onehsot": machine_task.oneshot,
                    "server": {
                        "provider": server.provider,
                        "dl": server.detail["dl"],
                        "ul": server.detail["ul"],
                        "ipv6": machine_task.detail["ipv6"],
                        "thread": machine_task.detail["thread"],
                    },
                }
                res["results"].append(r)
                res["count"] += 1
            return JsonResponse(res)
        except ValidationError as e:
            res = JsonResponse({"msg": e.message_dict})
            res.status_code = 400
            return res


class ResultView(View):
    async def post(self, request, *args, **kwargs):
        try:
            user, data = await aget_user_and_data(request)

            task_id = data.get("task_id")
            upload = data.get("upload")
            download = data.get("download")
            ping = data.get("ping")
            jitter = data.get("jitter")

            machine_task = await aget_object_or_none(MachineTask, pk=task_id)
            if not machine_task:
                raise ValidationError({"task_id": "Invalid"})

            machine = await aget_fk(machine_task, "machine")
            owner = await aget_fk(machine, "owner")
            if owner != user:
                raise ValidationError({"user": "Wrong user"})

            name = f"{machine_task.pk:0>3}"
            filename = f"data/{name[:3]}/{machine_task.pk}.rrd"
            await sync_to_async(update_rrd)(filename, upload, download, ping, jitter)

            if machine_task.oneshot:
                machine_task.state = MachineTask.State.FINISH
                await aclean_then_save_instance(machine_task)
            else:
                machine_task.state = MachineTask.State.WORK
                await aclean_then_save_instance(machine_task)

            return JsonResponse({"msg": "ok"})
        except ValidationError as e:
            res = JsonResponse({"msg": e.message_dict})
            res.status_code = 400
            return res
