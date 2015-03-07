"""
    kettle.message
    ~~~~~~~~~~~~~~

    Contains functionality for dealing with network messages.
"""
__all__ = ['MessageType', 'Message']


import collections
import enum

from kettle.exceptions import KettleMessageFormatError
from kettle.id import Id


class MessageType(enum.IntEnum):
    """
    Represents known types of messages used in the network.
    """

    request = 1
    response = 2
    error = 3


class Message:
    """
    Represents a payload sent between two peers on the network.
    """

    __slots__ = ('type', 'node_id', 'address', 'rpc', 'rpc_id', 'payload')

    @classmethod
    def request(cls, node_id, address, rpc, args):
        """
        Create message to request network for data.
        """
        rpc_id = Id.new_id()
        return cls(MessageType.request.name, node_id, address, rpc, rpc_id, args)

    @classmethod
    def response(cls, node_id, address, rpc, rpc_id, args):
        """
        Create message to respond to network request.
        """
        return cls(MessageType.response.name, node_id, address, rpc, rpc_id, args)

    # @classmethod
    # def error(cls, node_id, address, rpc, rpc_id, args):
    #     """
    #     """
    #     return cls(MessageType.error.name, node_id, address, rpc, rpc_id, args)

    @classmethod
    def encode(cls, msg):
        """
        """
        try:
            return msg.to_dict() if not isinstance(msg, collections.Mapping) else msg
        except Exception as e:
            raise KettleMessageFormatError('Invalid message attributes: {}'.format(e))

    @classmethod
    def decode(cls, **data):
        """
        """
        try:
            return cls(**data)
        except Exception as e:
            raise KettleMessageFormatError('Invalid message attributes: {}'.format(e))

    def __init__(self, type, node_id, address, rpc, rpc_id, payload):
        self.type = type
        self.node_id = node_id
        self.address = address
        self.rpc = rpc
        self.rpc_id = rpc_id
        self.payload = payload

    def __repr__(self):
        return '<{}(type={}, node_id={}, address={}, rpc={}, rpc_id={}, payload={})>'.format(self.__class__.__name__,
                                                                                             self.type,
                                                                                             self.node_id,
                                                                                             self.address,
                                                                                             self.rpc,
                                                                                             self.rpc_id,
                                                                                             self.payload)

    def __str__(self):
        direction = '>>>' if self.type == MessageType.request.name else '<<<'
        return '{} {} ({}, {}, {})'.format(direction, self.rpc, self.address, self.node_id, self.payload)

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

    def to_dict(self):
        return dict((a, getattr(self, a)) for a in self.__slots__)
