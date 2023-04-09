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
        ip_parts = obj.ip.split(".")
        return ".".join([ip_parts[0], "*", "*", ip_parts[-1]])


class TargetItem(Schema):
    id: int
    name: str
    created: datetime

    url: HttpUrl
    ipv6: bool


class TcpPingCreate(Schema):
    ping_min: float
    ping_jitter: float


class TcpPingData(Schema):
    created: datetime
    ping_min: float
    ping_jitter: float
