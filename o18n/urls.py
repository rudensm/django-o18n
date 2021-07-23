from django.conf import settings
from django.urls import LocalePrefixPattern, URLResolver
from django.utils.translation import get_language

def o18n_patterns(*urls, prefix_default_language=True):
    """
    Add the language code prefix to every URL pattern within this function.
    This may only be used in the root URLconf, not in an included URLconf.
    """
    if not settings.USE_I18N:
        return list(urls)
    return [
        URLResolver(
            CountryLocalePrefixPattern(prefix_default_language=prefix_default_language),
            list(urls),
        )
    ]

class CountryLocalePrefixPattern(LocalePrefixPattern):
    
    def match(self, path):
        language_prefix = self.language_prefix
        if language_prefix and path.startswith(language_prefix):
            return path[len(language_prefix):], (), {}
        return None
    
    @property
    def regex(self):
        # This is only used by reverse() and cached in _reverse_dict.
        return re.compile(self.language_prefix or "")
    
    @property
    def language_prefix(self):
        language_code = get_language() or settings.LANGUAGE_CODE
        # if not self.prefix_default_language:
        #     return ''
        # else:
        from .util import get_country_language_prefix
        return get_country_language_prefix()
