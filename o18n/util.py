import re
import warnings

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.dispatch import receiver
from django.test.signals import setting_changed
from django.utils.translation import get_language
from django.utils.translation.trans_real import get_supported_language_variant

country_language_prefix_re = re.compile(r'^/([a-z]{2})-(?:([A-Z]{2})/)?')
_language_maps = None


def get_countries_setting():
    """
    Return the O18N_COUNTRIES or COUNTRIES setting.

    The latter is more readable and more consistent with LANGUAGES.
    The former is less likely to clash with another application.
    """
    try:
        return settings.O18N_COUNTRIES
    except AttributeError:
        return settings.COUNTRIES


def _variant(country, language):
    language_code = '{}-{}'.format(language, country)
    try:
        return get_supported_language_variant(language_code)
    except LookupError:
        raise ImproperlyConfigured(
            "No matching locale found for '{}'. ".format(language_code) +
            "Check your COUNTRIES and LANGUAGES settings.")

def get_countries_by_language(language_code):
    countries = []
    for i in get_countries_setting():
        if language_code in i[1]:
            countries.append(i[0])
    return countries

def get_default_country_for_language(language):
    countries_by_language = get_countries_by_language(language)
    return countries_by_language[0] if countries_by_language else None

def get_language_maps():
    """
    Create a mapping of country -> URL language -> (language, language code).

    This allows checking for countries and languages efficiently.
    """
    global _language_maps
    if _language_maps is None:
        outer = {}
        for country, other_languages in get_countries_setting():
            main_language = other_languages[0]
            inner = {}
            for language in other_languages:
                inner[language] = language, _variant(country, language)
            outer[country] = inner
        _language_maps = outer
    return _language_maps


@receiver(setting_changed)
def reset_caches(**kwargs):
    global _language_maps
    if kwargs['setting'] in {'COUNTRIES', 'O18N_COUNTRIES', 'LANGUAGES'}:
        _language_maps = None

def get_country_language_from_request(request):
    """
    Return the country and language information when found in the path.
    """
    regex_match = country_language_prefix_re.match(request.path_info)
    if regex_match:
        language, country = regex_match.groups()
    else:
        language = get_language()
        country = get_default_country_for_language(language)
    return country.lower() if country else None, language

def get_country_language_prefix():
    """
    Return the URL prefix according to the current country and language.
    """
    language = get_language().split('-')[0]
    from .country import get_country        # avoid import loop
    country = get_country() or get_default_country_for_language(language)
    if country is None:

        language = settings.LANGUAGE_CODE
        country = get_default_country_for_language(language)
    language_map = get_language_maps()[country]
    if language in language_map:
        countries = get_countries_by_language(language)
        if len(countries) == 1:
            return language + "/"
        return "-".join((language, country.upper())) + "/"
    elif None in language_map and language_map[None][0] == language:
        return language
    return None
