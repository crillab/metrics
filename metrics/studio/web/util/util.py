import base64
import io
from typing import TextIO

from metrics.scalpel import CampaignParserListener


def create_listener(xp_ware, input, time) -> CampaignParserListener:
    listener = CampaignParserListener()
    listener.start_campaign()
    listener.log_data('timeout', '5000')
    listener.log_data('memout', '14400')
    listener.log_data('name', 'Campaign')
    listener.add_key_mapping('experiment_ware', xp_ware)
    listener.add_key_mapping('cpu_time', time)
    listener.add_key_mapping('input', input)
    return listener


def decode(contents) -> TextIO:
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    return io.StringIO(decoded.decode('utf-8'))


def have_parameter(pathname):
    return len(pathname.split('/')) > 2 and pathname.split('/')[-1] is not None and pathname.split('/')[-1] != ''
