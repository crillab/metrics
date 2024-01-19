# from https://stackoverflow.com/questions/3096860/convert-time-string-expressed-as-numbermhdsw-to-seconds-in-python
from datetime import timedelta
import re
UNITS = {'s': 'seconds', 'm': 'minutes', 'h': 'hours', 'd': 'days', 'w': 'weeks'}


def convert_to_seconds(text):
    return int(timedelta(**{
        UNITS.get(m.group('unit').lower(), 'seconds'): float(m.group('val'))
        for m in re.finditer(
            r'(?P<val>\d+(\.\d+)?)(?P<unit>[smhdw]?)',
            text.replace(' ', ''),
            flags=re.I
        )
    }).total_seconds())
