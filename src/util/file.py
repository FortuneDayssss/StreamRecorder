import json


def parse_file_size(file_size_str):
    if not file_size_str or len(file_size_str) == 0:
        return None
    if file_size_str[-1] == 'G':
        return int(file_size_str[:-1]) * 1024 * 1024 * 1024
    if file_size_str[-1] == 'M':
        return int(file_size_str[:-1]) * 1024 * 1024
    if file_size_str[-1] == 'K':
        return int(file_size_str[:-1]) * 1024
    return None


def load_json_from_file(file_name):
    try:
        with open(file_name, 'r', encoding="utf-8") as f:
            config_json = json.loads(f.read())
            return config_json
    except:
        return None
