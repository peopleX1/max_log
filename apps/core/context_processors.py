from django.conf import settings
from django.utils import translation


def settings_context(request):
    current_language = translation.get_language()
    return {
        'settings': settings,
        'language_options': [
            {'value': code, 'label': name, 'selected': code == current_language}
            for code, name in settings.LANGUAGES
        ],
    }
