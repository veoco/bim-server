from django.templatetags.static import static
from django.urls import reverse

from jinja2 import Environment

import mistune

markdown = mistune.create_markdown()


def environment(**options):
    env = Environment(**options)
    env.globals.update({"static": static, "url": reverse, "markdown": markdown})
    return env
