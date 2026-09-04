from django.utils import translation
from django.utils.cache import patch_vary_headers
from django.utils.deprecation import MiddlewareMixin


class UserLanguageMiddleware(MiddlewareMixin):
    def process_request(self, request):
        language = translation.get_language_from_request(request, check_path=False)
        translation.activate(language)
        request.LANGUAGE_CODE = translation.get_language()

    def process_response(self, request, response):
        patch_vary_headers(response, ('Accept-Language',))
        response.headers.setdefault('Content-Language', translation.get_language())
        return response
