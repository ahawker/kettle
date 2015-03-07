"""
    kettle
    ~~~~~~~

    Erecting a dispenser.

    :copyright: (c) 2015 by Andrew Hawker.
    :license: See LICENSE for more details.
"""
__name__ = 'kettle'
__author__ = 'Andrew Hawker <andrew.r.hawker@gmail.com>'
__license__ = '???'


import itertools


try:
    from __version__ import __version__
except ImportError:
    pass
else:
    __version__ = __version__


def get_event_loop():
    """
    Return the default `asyncio` event loop with conditional `create_task` patch
    for versions < 3.4.2.
    """
    import asyncio
    import signal
    import types

    loop = asyncio.get_event_loop()

    # Patch `create_task` method on loop if running older than 3.4.2.
    if not hasattr(loop, 'create_task'):
        loop.create_task = types.MethodType(lambda loop, coro: asyncio.async(coro, loop=loop), loop)

    return loop


from . import codec
from .codec import *
from . import connection
from .connection import *
from . import constants
from .constants import *
from . import exceptions
from .exceptions import *
from . import id
from .id import *
from . import message
from .message import *
from . import node
from .node import *
from . import peer
from .peer import *
from . import protocol
from .protocol import *
from . import routing
from .routing import *


__all__ = list(itertools.chain(codec.__all__,
                               connection.__all__,
                               constants.__all__,
                               exceptions.__all__,
                               id.__all__,
                               message.__all__,
                               node.__all__,
                               peer.__all__,
                               protocol.__all__,
                               routing.__all__))
