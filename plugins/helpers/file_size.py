#!/usr/bin/env python3
"""
Convert bytes to MB.... GB... etc
"""
import math


def convert_bytes(num):
    """
    This function will convert bytes to MB, GB, etc.
    """
    units = ['bytes', 'KB', 'MB', 'GB', 'TB']
    if num == 0:
        return '0 bytes'
    i = int(math.floor(math.log(num, 1024)))
    return "{:.1f} {}".format(num / (1024 ** i), units[i])

