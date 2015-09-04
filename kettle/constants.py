"""
    kettle.constants
    ~~~~~~~~~~~~~~~~

    Contains package level constants.
"""
__all__ = ['K', 'ALPHA', 'HASH_LENGTH', 'DEFAULT_REQUEST_TIMEOUT', 'ID_ENDIANNESS', 'ID_SIGNED']


import sys


#: Number of nodes to store per bucket.
K = 20


#: Number of parallel requests during node/value lookup.
ALPHA = 3


#: Size of the hash key.
HASH_LENGTH = 160


#: Default maximum of seconds a RPC request takes before error.
DEFAULT_REQUEST_TIMEOUT = 10


#: Endianness of the node/rpc id's.
ID_ENDIANNESS = sys.byteorder


#: Flag denoting if the node/rpc id's are signed/unsigned.
ID_SIGNED = False
