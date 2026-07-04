"""
Custom middleware for PHLMS project.
"""
from django.utils.deprecation import MiddlewareMixin


class NoCacheMiddleware(MiddlewareMixin):
    """
    Middleware to prevent browser caching for all pages.
    This prevents the back button from showing cached content after logout.
    """
    def process_response(self, request, response):
        # Only add no-cache headers if user is authenticated
        if hasattr(request, 'user') and request.user.is_authenticated:
            response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'
        return response
