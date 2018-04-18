import re

version_re = re.compile(r'^(\d+) \. (\d+) (\. (\d+))? ([ab](\d+))?$',
                        re.VERBOSE | re.ASCII)


def is_version(vstring):
    match = version_re.match(vstring)
    if not match:
        return False
    return True
