from django.conf import settings
from django.contrib.sessions.middleware import SessionMiddleware


class SessionCustomMiddleware(SessionMiddleware):
    def process_request(self, request):
        super().process_request(request)
        if not request.session.session_key:
            request.session.cycle_key()
