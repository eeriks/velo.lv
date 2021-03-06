from django.conf import settings
from django.contrib.sessions.middleware import SessionMiddleware


class CustomSessionMiddleware(SessionMiddleware):
    def process_response(self, request, response):
        if getattr(request, "user", None) and request.user.is_anonymous() and "login" not in request.path:
            if settings.SESSION_COOKIE_NAME in request.COOKIES:
                response.delete_cookie(settings.SESSION_COOKIE_NAME)
            if "messages" in request.COOKIES:
                response.delete_cookie("messages")
            del response['Vary']  # remove vary on cookies etc for anonymous users.
            return response
        return super().process_response(request, response)
