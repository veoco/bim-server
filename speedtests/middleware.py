import base64, asyncio

from django.utils.decorators import async_only_middleware

from .models import User


@async_only_middleware
def token_auth_middleware(get_response):

    async def middleware(request):
        header = request.headers.get("Authorization")
        if header and header.startswith("Basic "):
            _, b64 = header.split(' ', 1)
            try:
                text = base64.b64decode(b64).decode('utf-8')
                if ':' in text:
                    email, token = text.split(':', 1)
                    user = await User.objects.aget(email=email, token=token)
                    request.user = user
            except:
                pass
        response = await get_response(request)
        return response

    return middleware
