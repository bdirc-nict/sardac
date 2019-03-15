# coding: utf-8

# Copyright (c) 2019 National Institute of Information and Communications Technology
# Released under the GPLv2 license

_mgp_data = {}


def read_mgp_info(file_key, file):
    """
    Read info file.
    :param file_key: Key
    :param file: Path of info file
    """
    tmp = {}
    for l in open(file, "r"):
        key, value = l.split("=", maxsplit=1)
        tmp[key.strip()] = value.strip()
    _mgp_data[file_key] = tmp

def get_data(filekey, itemkey):
    """
    Get value for specified key.
    :param filekey: Key
    :param itemkey: Key
    :return: Value
    """
    return _mgp_data[filekey][itemkey]


def get_decimal_from_sexagesimal(exp):
    """
    Translate sexagesimal degree into decimal.
    :param exp: sexagesimal degree
    :return: degree value
    """
    items = exp.split(":")
    tmp = 0
    for v in reversed(items):
        tmp = float(v) + tmp / 60
    return tmp
