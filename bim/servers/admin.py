from django.contrib import admin

from .models import Machine, Server, Task

admin.site.register(Machine)
admin.site.register(Server)
admin.site.register(Task)
