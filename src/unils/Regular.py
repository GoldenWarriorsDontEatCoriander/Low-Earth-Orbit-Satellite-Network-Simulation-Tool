import re


USERID_PATTERN = rb'\[userid:([^\]]+)\]'
SATELLITEID_PATTERN = rb'\[satelliteid:([^\]]+)\]'
USERNAME_PATTERN = rb'\[username:([^\]]+)\]'
PASSWORD_PATTERN = rb'\[password:([^\]]+)\]'
ACCESS_STATE_PATTERN = rb'\[access_state:([^\]]+)\]'
SESSION_PATTERN = rb'\[session:([^\]]+)\]'
SWITCH_STATE_PATTERN = rb'\[switch_state:([^\]]+)\]'
HAS_ROUTING_PATH_PATTERN = rb'\[has_routing_path:([^\]]+)\]'
STATE_PATH_PATTERN = rb'\[state:([^\]]+)\]'

def get_attribute_from_message(PATTERN, message):
    match = re.search(PATTERN, message)
    return match.group(1).decode()

def get_routing_path_from_message(message):
    ip_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
    ip_list = re.findall(ip_pattern, message)
    del ip_list[0]
    del ip_list[0]
    return ip_list