"""Unconditional CORS middleware so the Flutter web/desktop app can call the API.

corsheaders 4.9 does not reliably honour CORS_ALLOWED_ORIGINS=['*']
with Django 5.2, which blocked the browser's preflight and every
cross-origin API call (the web build could never log in). This tiny
middleware echoes the calling Origin, handles OPTIONS preflights, and
attaches the CORS headers to every response (including 401s) so the
mobile app authenticates with a bearer token from any origin.
"""
from django.http import HttpResponse


class CorsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if (
            request.method == 'OPTIONS'
            and request.headers.get('Origin')
        ):
            return self._preflight(request)
        response = self.get_response(request)
        self._add_headers(request, response)
        return response

    def _preflight(self, request):
        resp = HttpResponse()
        self._add_headers(request, resp)
        resp['Access-Control-Allow-Methods'] = (
            'GET, POST, PUT, PATCH, DELETE, OPTIONS'
        )
        requested = request.headers.get('Access-Control-Request-Headers', '')
        resp['Access-Control-Allow-Headers'] = (
            requested or 'Content-Type, Authorization'
        )
        resp['Access-Control-Max-Age'] = '86400'
        return resp

    def _add_headers(self, request, response):
        origin = request.headers.get('Origin')
        if not origin:
            return
        response['Access-Control-Allow-Origin'] = origin
        response['Vary'] = 'Origin'
        response['Access-Control-Allow-Credentials'] = 'true'
