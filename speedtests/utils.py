import json, random, string, datetime

import rrdtool

from pathlib import Path

from asgiref.sync import sync_to_async
from django.contrib.auth import get_user_model, authenticate, login, logout
from django.core.exceptions import ValidationError


async def aget_object_or_none(klass, *args, **kwargs):
    try:
        instance = await klass.objects.aget(*args, **kwargs)
        return instance
    except:
        return None


def get_json_or_none(request):
    res = False
    if request.content_type == "application/json":
        try:
            res = json.loads(request.body)
        except json.JSONDecodeError:
            res = None
    return res


def generate_token():
    letters = string.ascii_lowercase
    return "".join([random.choice(letters) for _ in range(30)])


async def aclean_then_save_instance(instance):
    def _fn(instance):
        instance.full_clean()
        instance.save()

    return await sync_to_async(_fn)(instance)


async def aget_request_user_or_none(request):
    def _fn(request):
        return request.user if request.user.is_authenticated else None

    return await sync_to_async(_fn)(request)


async def aget_fk(obj, fk_name):
    def _fn(obj, fk_name):
        return getattr(obj, fk_name)

    return await sync_to_async(_fn)(obj, fk_name)


async def aget_user_and_data(request):
    user = await aget_request_user_or_none(request)
    if not user:
        raise ValidationError({"user": "Login required"})

    data = get_json_or_none(request)
    if not data:
        raise ValidationError({"fields": "Empty fields"})

    return user, data


def create_user(username, email, password):
    User = get_user_model()
    token = generate_token()
    user = User(username=username, email=email, token=token)
    user.set_password(password)
    user.full_clean()
    user.save()


def authenticate_user(request, username, password):
    return authenticate(request, username=username, password=password)


def user_login(request, user):
    login(request, user)


def user_logout(request):
    logout(request)


def create_rrd(filename):
    path = Path(filename)
    parent = path.parent
    if not parent.exists():
        parent.mkdir(parents=True)
    now = datetime.datetime.now() - datetime.timedelta(hours=1)
    hour = datetime.datetime(now.year, now.month, now.day, now.hour)
    rrdtool.create(
        str(path),
        "--start",
        f"{int(hour.timestamp())}",
        "--step",
        "3600",
        "DS:upload:GAUGE:3600:0:10000",
        "DS:download:GAUGE:3600:0:10000",
        "DS:ping:GAUGE:3600:0:1000",
        "DS:jitter:GAUGE:3600:0:1000",
        "RRA:AVERAGE:0.5:1:30h",
        "RRA:AVERAGE:0.5:1:10d",
        "RRA:AVERAGE:0.5:24:360d",
    )


def update_rrd(filename, upload, download, ping, jitter):
    try:
        upload = float(upload)
        download = float(download)
        ping = float(ping)
        jitter = float(jitter)
        now = datetime.datetime.now()
        hour = datetime.datetime(now.year, now.month, now.day, now.hour)
        rrdtool.update(
            str(filename), f"{int(hour.timestamp())}:{upload}:{download}:{ping}:{jitter}"
        )
    except:
        raise ValidationError({"fields": "Invalid"})


def fetch_rrd(filename, resolution, start, end="now"):
    result = rrdtool.fetch(
        str(filename),
        "AVERAGE",
        "-r",
        resolution,
        "-s",
        start,
        "-e",
        end,
    )
    start, end, step = result[0]
    rows = result[2]

    res = []
    i = 0
    while start < end:
        start += step
        upload = round(rows[i][0], 2) if rows[i][0] else rows[i][0]
        download = round(rows[i][1], 2) if rows[i][1] else rows[i][1]
        ping = round(rows[i][2], 2) if rows[i][2] else rows[i][2]
        jitter = round(rows[i][3], 2) if rows[i][3] else rows[i][3]
        res.append((start, upload, download, ping, jitter))
        i += 1
    return res
