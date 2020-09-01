import pytz
from django.utils import timezone
from django.contrib.sessions.middleware import SessionMiddleware
from django.utils.deprecation import MiddlewareMixin


class SessionCustomMiddleware(SessionMiddleware):
    def process_request(self, request):
        super().process_request(request)
        if not request.session.session_key:
            request.session.cycle_key()
            request.session['django_timezone'] = 'Europe/Moscow'


class TimezoneMiddleware(MiddlewareMixin):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        tzname = request.session.get('django_timezone')
        if tzname:
            timezone.activate(pytz.timezone(tzname))
        else:
            timezone.deactivate()
        return self.get_response(request)
