from typing import Union, Optional

from fluent.runtime import FluentLocalization, FluentResourceLoader

from config import locales_path

lang_codes = [_.name for _ in locales_path.iterdir() if locales_path.joinpath(_).is_dir()]

loader = FluentResourceLoader(str(locales_path.joinpath("{locale}")))
locales = dict(zip(lang_codes, [FluentLocalization([_], ["main.ftl"], loader) for _ in lang_codes]))

print(loader)
print(lang_codes)


def get_text(lang_code: str, key) -> str:
    """
    Returning text by key

    :param lang_code: ISO 639-1 locale code
    :param key: Text key
    :return: Text
    :raises: ValueError
    """
    print(locales)
    return locales.get(lang_code, locales['ru']).format_value(key)


print(get_text('uz', 'greeting'))