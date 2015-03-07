"""
    kettle.exceptions
    ~~~~~~~~~~~~~~~~~

    Contains custom exceptions used by Kettle.
"""
__all__ = ['KettleError', 'KettleConnectionError', 'KettleConnectionClosed',
           'KettleRpcError', 'KettleRpcTimeout', 'KettleMessageFormatError']


class KettleError(Exception):
    pass


class KettleConnectionError(KettleError):
    pass


class KettleConnectionClosed(KettleConnectionError):
    pass


class KettleRpcError(KettleError):
    pass


class KettleRpcTimeout(KettleRpcError):
    pass


class KettleMessageFormatError(KettleError):
    pass
