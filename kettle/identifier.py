__author__ = 'Andrew Hawker <andrew.r.hawker@gmail.com>'

import hashlib
import random

def unique_identifier():
    return int(hashlib.sha1(str(random.getrandbits(160))).hexdigest(), 16)