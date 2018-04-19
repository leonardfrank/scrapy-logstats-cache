import re
from contextlib import contextmanager

from scrapy.settings import Settings

version_re = re.compile(r'^(\d+) \. (\d+) (\. (\d+))? ([ab](\d+))?$',
                        re.VERBOSE | re.ASCII)


def is_version(vstring: str) -> bool:
    match = version_re.match(vstring)
    if not match:
        return False
    return True


@contextmanager
def unfreeze_settings(settings: Settings):
    orig_status = settings.frozen
    settings.frozen = False
    try:
        yield settings
    finally:
        settings.frozen = orig_status
