"""
    kettle.log
    ~~~~~~~~~~

    Contains Kettle logging.
"""
__all__ = ['LOGGER']


import logging

from kettle.meta import resolve_type


def create_logger(name=None):
    """
    Creates a new logger instance tagged with the given name.
    """

    class KettleLogger(logging.getLoggerClass()):
        """
        Extends the python standard logger to automatically resolve child object type names.
        """

        def child(self, obj):
            """
            Return a :class: `~kettle.log.KettleLogger` instance attached as a child
            to this logger keyed by tag.
            """
            child = super(KettleLogger, self).getChild(resolve_type(obj))
            child.__class__ = KettleLogger
            return child

    # Configure new Kettle logger.
    logger = logging.getLogger(name)
    logger.__class__ = KettleLogger
    return logger


LOGGER = create_logger()
