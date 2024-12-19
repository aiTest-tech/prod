from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
from django.utils.deprecation import MiddlewareMixin

class HideSensitiveHeadersMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        # Remove the 'Host' header from the response (although it's sent by the client, not your server)
        response.headers.pop("Host", None)
        return response
    
class XXSSProtectionMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        response['X-XSS-Protection'] = '1; mode=block'
        return response

class SecurityHeadersMiddleware:
    """
    Middleware to add custom security headers.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Add Permissions-Policy header
        response["Permissions-Policy"] = getattr(
            settings, "SECURE_PERMISSION_POLICY", "geolocation=(), microphone=(), camera=()"
        )

        return response

class CacheControlMiddleware:
    """
    Middleware to enforce caching policies for responses.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Process the request and get the response
        response = self.get_response(request)

        # Add caching headers to the response
        response["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response["Pragma"] = "no-cache"
        response["Expires"] = "0"

        return response

class RemoveHostnameMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Call the view and get the response
        response = self.get_response(request)

        # Remove the 'Host' header from the response if it exists
        if 'Host' in response.headers:
            del response.headers['Host']

        # Optionally remove any other headers that might include the hostname
        # For example, remove Location header if it contains the hostname
        if 'Location' in response.headers:
            location = response.headers['Location']
            if '://localhost' in location:
                response.headers['Location'] = location.replace('localhost', 'your-new-hostname.com')

        return response

from django.utils.deprecation import MiddlewareMixin

class SanitizeHeadersMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # Remove or mask sensitive headers
        if "HTTP_REFERER" in request.META:
            request.META["HTTP_REFERER"] = "[HIDDEN]"
        if "HTTP_ORIGIN" in request.META:
            request.META["HTTP_ORIGIN"] = "[HIDDEN]"
        return None

    def process_response(self, request, response):
        # Optionally sanitize response headers
        return response

class HideHostHeaderMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        # Remove the 'Host' header from the response (if desired)
        response.headers.pop('Host', None)
        return response