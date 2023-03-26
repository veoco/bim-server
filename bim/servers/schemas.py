from datetime import datetime

from ninja import Schema, Field
from pydantic import HttpUrl


class Message(Schema):
    msg: str


class IdMessage(Schema):
    id: str


class MachineCreate(Schema):
    token: str = Field(min_length=5, max_length=64)
    name: str = Field(min_length=1, max_length=16)


class MachineItem(Schema):
    id: int
    token: str
    name: str
    ip: str

    created: datetime
    modified: datetime
    status: str

    @staticmethod
    def resolve_ip(obj):
        ip_parts = obj.ip.split(".")
        return ".".join([ip_parts[0], "*", '*',ip_parts[-1]])


class ServerCreate(Schema):
    token: str = Field(min_length=5, max_length=64)
    name: str = Field(min_length=1, max_length=16)
    download_url: HttpUrl
    upload_url: HttpUrl
    ipv6: bool
    multi: bool


class ServerItem(Schema):
    id: int
    token: str
    name: str

    created: datetime
    modified: datetime

    download_url: HttpUrl
    upload_url: HttpUrl
    ipv6: bool
    multi: bool


class TaskFinish(Schema):
    download: float
    download_status: str = Field(min_length=1, max_length=16)
    upload: float
    upload_status: str = Field(min_length=1, max_length=16)
    latency: float
    jitter: float

class TaskWithMachineAndServerItem(Schema):
    id: int 

    machine: MachineItem
    server: ServerItem

    created: datetime
    modified: datetime
    status: str

    download: float
    download_status: str
    upload: float
    upload_status:str
    latency: float
    jitter: float
