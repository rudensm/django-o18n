from django.conf import settings
from django.conf.urls.i18n import is_language_prefix_patterns_used
from django.utils import translation
from django.middleware.locale import LocaleMiddleware

class CountryLocaleMiddleware(LocaleMiddleware):
    
    def process_request(self, request):
        super().process_request(request)
        from .util import get_country_language
        request.COUNTRY = get_country_language(request)[0]
        from . import country as country_mod
        try:
            country_mod.activate(request.COUNTRY)
        except ValueError:
            translation.activate(settings.LANGUAGE_CODE)
            request.LANGUAGE_CODE = translation.get_language()
            request.COUNTRY = None
