"""
    kettle.constants
    ~~~~~~~~~~~~~~~~

    Contains package level constants.
"""
__all__ = ['K', 'ALPHA', 'HASH_LENGTH', 'DEFAULT_REQUEST_TIMEOUT']


#: Number of nodes to store per bucket.
K = 20


#: Number of parallel requests during node/value lookup.
ALPHA = 3


#: Size of the hash key.
HASH_LENGTH = 160


#: Default maximum of seconds a RPC request takes before error.
DEFAULT_REQUEST_TIMEOUT = 10