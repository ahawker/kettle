"""
    kettle.codec
    ~~~~~~~~~~~~

    Contains codecs for serializing communication messages.
"""
__all__ = ['CodecError', 'Codec', 'JSONCodec', 'PickleCodec']


import json
import pickle


class CodecError(Exception):
    pass


class Codec:
    """

    """

    def __init__(self, encoding='utf-8', errors='strict'):
        self.encoding = encoding
        self.errors = errors

    def encode(self, data):
        return data.encode(self.encoding, self.errors)

    def decode(self, data):
        return data.decode(self.encoding, self.errors)


class JSONCodec(Codec):
    """

    """
    def encode(self, data):
        data = json.dumps(data)
        return super().encode(data)

    def decode(self, data):
        data = super().decode(data)
        return json.loads(data)


class PickleCodec(Codec):
    """

    """
    def encode(self, data):
        return pickle.dumps(data)

    def decode(self, data):
        return pickle.loads(data, encoding=self.encoding, errors=self.errors)
