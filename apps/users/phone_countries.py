import re

from django.templatetags.static import static
from django.utils import translation

NAME_LANGUAGES = ('ru', 'en', 'es', 'pt', 'uz', 'fr')

COUNTRIES = [
    {'iso2': 'RU', 'dial': '+7', 'placeholder': '123 456 78 90', 'names': {'ru': 'Россия', 'en': 'Russia', 'es': 'Rusia', 'pt': 'Rússia', 'uz': 'Rossiya', 'fr': 'Russie'}},
    {'iso2': 'BY', 'dial': '+375', 'placeholder': '12 345 6789', 'names': {'ru': 'Беларусь', 'en': 'Belarus', 'es': 'Bielorrusia', 'pt': 'Belarus', 'uz': 'Belarusiya', 'fr': 'Biélorussie'}},
    {'iso2': 'AZ', 'dial': '+994', 'placeholder': '12 345 6789', 'names': {'ru': 'Азербайджан', 'en': 'Azerbaijan', 'es': 'Azerbaiyán', 'pt': 'Azerbaijão', 'uz': 'Ozarbayjon', 'fr': 'Azerbaïdjan'}},
    {'iso2': 'AM', 'dial': '+374', 'placeholder': '12 345 678', 'names': {'ru': 'Армения', 'en': 'Armenia', 'es': 'Armenia', 'pt': 'Armênia', 'uz': 'Armaniston', 'fr': 'Arménie'}},
    {'iso2': 'GE', 'dial': '+995', 'placeholder': '123 45 67 89', 'names': {'ru': 'Грузия', 'en': 'Georgia', 'es': 'Georgia', 'pt': 'Geórgia', 'uz': 'Gruziya', 'fr': 'Géorgie'}},
    {'iso2': 'KZ', 'dial': '+7', 'placeholder': '123 456 78 90', 'names': {'ru': 'Казахстан', 'en': 'Kazakhstan', 'es': 'Kazajistán', 'pt': 'Cazaquistão', 'uz': 'Qozog‘iston', 'fr': 'Kazakhstan'}},
    {'iso2': 'KG', 'dial': '+996', 'placeholder': '123 456 789', 'names': {'ru': 'Кыргызстан', 'en': 'Kyrgyzstan', 'es': 'Kirguistán', 'pt': 'Quirguistão', 'uz': 'Qirg‘iziston', 'fr': 'Kirghizistan'}},
    {'iso2': 'MD', 'dial': '+373', 'placeholder': '12 345 678', 'names': {'ru': 'Молдова', 'en': 'Moldova', 'es': 'Moldavia', 'pt': 'Moldova', 'uz': 'Moldova', 'fr': 'Moldavie'}},
    {'iso2': 'TJ', 'dial': '+992', 'placeholder': '12 345 6789', 'names': {'ru': 'Таджикистан', 'en': 'Tajikistan', 'es': 'Tayikistán', 'pt': 'Tajiquistão', 'uz': 'Tojikiston', 'fr': 'Tadjikistan'}},
    {'iso2': 'UZ', 'dial': '+998', 'placeholder': '12 345 6789', 'names': {'ru': 'Узбекистан', 'en': 'Uzbekistan', 'es': 'Uzbekistán', 'pt': 'Uzbequistão', 'uz': 'O‘zbekiston', 'fr': 'Ouzbékistan'}},
    {'iso2': 'AE', 'dial': '+971', 'placeholder': '12 345 6789', 'names': {'ru': 'ОАЭ Объединённые Арабские Эмираты', 'en': 'UAE United Arab Emirates', 'es': 'EAU Emiratos Árabes Unidos', 'pt': 'EAU Emirados Árabes Unidos', 'uz': 'BAA Birlashgan Arab Amirliklari', 'fr': 'EAU Émirats arabes unis'}},
    {'iso2': 'AF', 'dial': '+93', 'placeholder': '12 345 6789', 'names': {'ru': 'Афганистан', 'en': 'Afghanistan', 'es': 'Afganistán', 'pt': 'Afeganistão', 'uz': 'Afg‘oniston', 'fr': 'Afghanistan'}},
    {'iso2': 'BO', 'dial': '+591', 'placeholder': '1 234 5678', 'names': {'ru': 'Боливия', 'en': 'Bolivia', 'es': 'Bolivia', 'pt': 'Bolívia', 'uz': 'Boliviya', 'fr': 'Bolivie'}},
    {'iso2': 'CD', 'dial': '+243', 'placeholder': '123 456 789', 'names': {'ru': 'Конго - Киншаса', 'en': 'Congo - Kinshasa', 'es': 'Congo - Kinshasa', 'pt': 'Congo - Kinshasa', 'uz': 'Kongo - Kinshasa', 'fr': 'Congo - Kinshasa'}},
    {'iso2': 'CG', 'dial': '+242', 'placeholder': '12 345 6789', 'names': {'ru': 'Конго - Браззавиль', 'en': 'Congo - Brazzaville', 'es': 'Congo - Brazzaville', 'pt': 'Congo - Brazzaville', 'uz': 'Kongo - Brazzavil', 'fr': 'Congo - Brazzaville'}},
    {'iso2': 'CO', 'dial': '+57', 'placeholder': '123 456 7890', 'names': {'ru': 'Колумбия', 'en': 'Colombia', 'es': 'Colombia', 'pt': 'Colombia', 'uz': 'Kolumbiya', 'fr': 'Colombie'}},
    {'iso2': 'CU', 'dial': '+53', 'placeholder': '1 234 5678', 'names': {'ru': 'Куба', 'en': 'Cuba', 'es': 'Cuba', 'pt': 'Cuba', 'uz': 'Kuba', 'fr': 'Cuba'}},
    {'iso2': 'EG', 'dial': '+20', 'placeholder': '12 3456 7890', 'names': {'ru': 'Египет', 'en': 'Egypt', 'es': 'Egipto', 'pt': 'Egito', 'uz': 'Misr', 'fr': 'Égypte'}},
    {'iso2': 'GD', 'dial': '+1473', 'placeholder': '123 4567', 'names': {'ru': 'Гренада', 'en': 'Grenada', 'es': 'Granada', 'pt': 'Granada', 'uz': 'Grenada', 'fr': 'Grenade'}},
    {'iso2': 'ID', 'dial': '+62', 'placeholder': '123 4567 8901', 'names': {'ru': 'Индонезия', 'en': 'Indonesia', 'es': 'Indonesia', 'pt': 'Indonésia', 'uz': 'Indoneziya', 'fr': 'Indonésie'}},
    {'iso2': 'IN', 'dial': '+91', 'placeholder': '12345 67890', 'names': {'ru': 'Индия', 'en': 'India', 'es': 'India', 'pt': 'Índia', 'uz': 'Hindiston', 'fr': 'Inde'}},
    {'iso2': 'IQ', 'dial': '+964', 'placeholder': '123 456 7890', 'names': {'ru': 'Ирак', 'en': 'Iraq', 'es': 'Irak', 'pt': 'Iraque', 'uz': 'Iroq', 'fr': 'Irak'}},
    {'iso2': 'KH', 'dial': '+855', 'placeholder': '12 345 678', 'names': {'ru': 'Камбоджа', 'en': 'Cambodia', 'es': 'Camboya', 'pt': 'Camboja', 'uz': 'Kambodja', 'fr': 'Cambodge'}},
    {'iso2': 'KN', 'dial': '+1869', 'placeholder': '123 4567', 'names': {'ru': 'Сент-Китс и Невис', 'en': 'Saint Kitts and Nevis', 'es': 'San Cristóbal y Nieves', 'pt': 'São Cristóvão e Nevis', 'uz': 'Sent-Kits va Nevis', 'fr': 'Saint-Christophe-et-Niévès'}},
    {'iso2': 'KW', 'dial': '+965', 'placeholder': '1234 5678', 'names': {'ru': 'Кувейт', 'en': 'Kuwait', 'es': 'Kuwait', 'pt': 'Kuweit', 'uz': 'Quvayt', 'fr': 'Koweït'}},
    {'iso2': 'LA', 'dial': '+856', 'placeholder': '12 34 567 890', 'names': {'ru': 'Лаос', 'en': 'Laos', 'es': 'Laos', 'pt': 'Laos', 'uz': 'Laos', 'fr': 'Laos'}},
    {'iso2': 'LB', 'dial': '+961', 'placeholder': '1 234 567', 'names': {'ru': 'Ливан', 'en': 'Lebanon', 'es': 'Líbano', 'pt': 'Líbano', 'uz': 'Livan', 'fr': 'Liban'}},
    {'iso2': 'MM', 'dial': '+95', 'placeholder': '1 234 567 890', 'names': {'ru': 'Мьянма (Бирма)', 'en': 'Myanmar (Burma)', 'es': 'Myanmar (Birmania)', 'pt': 'Mianmar (Birmânia)', 'uz': 'Myanma (Birma)', 'fr': 'Myanmar (Birmanie)'}},
    {'iso2': 'MY', 'dial': '+60', 'placeholder': '12 345 6789', 'names': {'ru': 'Малайзия', 'en': 'Malaysia', 'es': 'Malasia', 'pt': 'Malásia', 'uz': 'Malayziya', 'fr': 'Malaisie'}},
    {'iso2': 'NI', 'dial': '+505', 'placeholder': '1234 5678', 'names': {'ru': 'Никарагуа', 'en': 'Nicaragua', 'es': 'Nicaragua', 'pt': 'Nicarágua', 'uz': 'Nikaragua', 'fr': 'Nicaragua'}},
    {'iso2': 'PK', 'dial': '+92', 'placeholder': '123 456 7890', 'names': {'ru': 'Пакистан', 'en': 'Pakistan', 'es': 'Pakistán', 'pt': 'Paquistão', 'uz': 'Pokiston', 'fr': 'Pakistan'}},
    {'iso2': 'PW', 'dial': '+680', 'placeholder': '123 4567', 'names': {'ru': 'Палау', 'en': 'Palau', 'es': 'Palaos', 'pt': 'Palau', 'uz': 'Palau', 'fr': 'Palaos'}},
    {'iso2': 'QA', 'dial': '+974', 'placeholder': '1234 5678', 'names': {'ru': 'Катар', 'en': 'Qatar', 'es': 'Catar', 'pt': 'Catar', 'uz': 'Qatar', 'fr': 'Qatar'}},
    {'iso2': 'SA', 'dial': '+966', 'placeholder': '12 345 6789', 'names': {'ru': 'Саудовская Аравия', 'en': 'Saudi Arabia', 'es': 'Arabia Saudita', 'pt': 'Arábia Saudita', 'uz': 'Saudiya Arabistoni', 'fr': 'Arabie saoudite'}},
    {'iso2': 'TH', 'dial': '+66', 'placeholder': '12 345 6789', 'names': {'ru': 'Таиланд', 'en': 'Thailand', 'es': 'Tailandia', 'pt': 'Tailândia', 'uz': 'Tailand', 'fr': 'Thaïlande'}},
    {'iso2': 'TM', 'dial': '+993', 'placeholder': '12 345 678', 'names': {'ru': 'Туркменистан', 'en': 'Turkmenistan', 'es': 'Turkmenistán', 'pt': 'Turcomenistão', 'uz': 'Turkmaniston', 'fr': 'Turkménistan'}},
    {'iso2': 'TR', 'dial': '+90', 'placeholder': '123 456 7890', 'names': {'ru': 'Турция', 'en': 'Turkey', 'es': 'Turquía', 'pt': 'Turquia', 'uz': 'Turkiya', 'fr': 'Turquie'}},
    {'iso2': 'TZ', 'dial': '+255', 'placeholder': '123 456 789', 'names': {'ru': 'Танзания', 'en': 'Tanzania', 'es': 'Tanzania', 'pt': 'Tanzânia', 'uz': 'Tanzaniya', 'fr': 'Tanzanie'}},
    {'iso2': 'VE', 'dial': '+58', 'placeholder': '123 456 7890', 'names': {'ru': 'Венесуэла', 'en': 'Venezuela', 'es': 'Venezuela', 'pt': 'Venezuela', 'uz': 'Venesuela', 'fr': 'Venezuela'}},
    {'iso2': 'VN', 'dial': '+84', 'placeholder': '12 345 6789', 'names': {'ru': 'Вьетнам', 'en': 'Vietnam', 'es': 'Vietnam', 'pt': 'Vietnã', 'uz': 'Vetnam', 'fr': 'Vietnam'}},
    {'iso2': 'BR', 'dial': '+55', 'placeholder': '12 34567 8901', 'names': {'ru': 'Бразилия', 'en': 'Brazil', 'es': 'Brasil', 'pt': 'Brasil', 'uz': 'Braziliya', 'fr': 'Brésil'}},
    {'iso2': 'CN', 'dial': '+86', 'placeholder': '123 4567 8901', 'names': {'ru': 'Китай', 'en': 'China', 'es': 'China', 'pt': 'China', 'uz': 'Xitoy', 'fr': 'Chine'}},
    {'iso2': 'GM', 'dial': '+220', 'placeholder': '123 4567', 'names': {'ru': 'Гамбия', 'en': 'Gambia', 'es': 'Gambia', 'pt': 'Gâmbia', 'uz': 'Gambiya', 'fr': 'Gambie'}},
    {'iso2': 'ZA', 'dial': '+27', 'placeholder': '12 345 6789', 'names': {'ru': 'ЮАР', 'en': 'South Africa', 'es': 'Sudáfrica', 'pt': 'África do Sul', 'uz': 'Janubiy Afrika Respublikasi', 'fr': 'Afrique du Sud'}},
]


def country_name_ru(iso2):
    for country in COUNTRIES:
        if country['iso2'] == iso2:
            return country['names']['ru']
    return iso2


def flag_url(iso2):
    return static(f'images/flags/{iso2.upper()}.webp')


def mask_from_placeholder(placeholder):
    return re.sub(r'\d', '0', placeholder)


def apply_mask(digits, mask):
    result = []
    digit_index = 0
    for char in mask:
        if digit_index >= len(digits):
            break
        if char == '0':
            result.append(digits[digit_index])
            digit_index += 1
        else:
            result.append(char)
    return ''.join(result)


def find_country(dial=None, name_ru=None):
    if name_ru:
        for country in COUNTRIES:
            if country['names']['ru'] == name_ru:
                return country
    if dial:
        for country in sorted(COUNTRIES, key=lambda c: -len(c['dial'])):
            if dial.startswith(country['dial']):
                return country
    return None


def name_language(language=None):
    language = (language or translation.get_language() or 'ru').lower()
    if language in NAME_LANGUAGES:
        return language
    base = language.split('-')[0]
    return base if base in NAME_LANGUAGES else 'ru'


def get_country_options(selected_iso2='RU', language=None):
    lang = name_language(language)
    return [
        {
            'value': country['iso2'],
            'label': country['names'][lang],
            'dial_code': country['dial'],
            'flag': flag_url(country['iso2']),
            'placeholder': country['placeholder'],
            'mask': mask_from_placeholder(country['placeholder']),
            'selected': country['iso2'] == selected_iso2,
        }
        for country in COUNTRIES
    ]
