from datetime import datetime

from ninja import Schema, Field
from pydantic import HttpUrl


class Message(Schema):
    msg: str


class MachineCreate(Schema):
    name: str = Field(min_length=1, max_length=32)


class MachineItem(Schema):
    id: int
    name: str
    ip: str

    created: datetime

    @staticmethod
    def resolve_ip(obj):
        ipv4 = True if "." in obj.ip else False
        if ipv4:
            parts = obj.ip.split(".")
            ip = ".".join(parts[:2]) + ".*.*"
        else:
            parts = obj.ip.split(":")
            if len(parts) > 4:
                prefix = ":".join(parts[:-4])
            elif len(parts) > 1:
                prefix = ":".join(parts[:-1])
            else:
                prefix = obj.ip
            ip = prefix+"::*"

        return ip


class TargetWorkerItem(Schema):
    id: int
    name: str
    created: datetime

    url: HttpUrl
    ipv6: bool


class TargetItem(Schema):
    id: int
    name: str
    created: datetime

    ipv6: bool


class TcpPingCreate(Schema):
    ping_min: float
    ping_jitter: float
    ping_failed: int


class TcpPingData(Schema):
    created: datetime
    ping_min: float
    ping_jitter: float
    ping_failed: int


class MachineWithTargets(Schema):
    detail: MachineItem
    targets: list[TargetItem]
