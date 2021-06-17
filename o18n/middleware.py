from django.conf import settings
from django.conf.urls.i18n import is_language_prefix_patterns_used
from django.middleware.locale import LocaleMiddleware
from django.shortcuts import redirect
from django.utils import translation
import re

class CountryLocaleMiddleware(LocaleMiddleware):
    
    def process_request(self, request):
        super().process_request(request)
        language_from_path = translation.get_language_from_path(request.path_info)
        if not language_from_path:
            return
        from .util import get_country_language_from_request
        request.COUNTRY, language_code = get_country_language_from_request(request)
        from . import country as country_mod
        try:
            country_mod.activate(request.COUNTRY)
        except ValueError:
            from .util import get_default_country_for_language
            request.COUNTRY = get_default_country_for_language(request.LANGUAGE_CODE)
        from .util import get_country_language_prefix
        path_info = request.path_info
        if not path_info.endswith("/"):
            path_info = path_info + "/"
        country_language_prefix = get_country_language_prefix()
        if not country_language_prefix or country_language_prefix not in path_info:
            path = path_info
            if re.search("^/[a-z]{2}/", path_info):
                path = re.sub("^/[a-z]{2}/", "/{}".format(country_language_prefix), path_info)
            elif re.search("^/[a-z]{2}-[a-z]{2}/", path_info):
                path = re.sub("^/[a-z]{2}-[a-z]{2}/", "/{}".format(country_language_prefix), path_info)
            if request.GET.urlencode():
                path = "{}?{}".format(path, request.GET.urlencode())
            return redirect(path)
