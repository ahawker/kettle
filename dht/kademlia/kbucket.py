__author__ = 'ahawker'

import itertools

class KBucket(object):
    def __init__(self, k=20):
        super(KBucket, self).__init__()
        self.k = k
        self.bucket = []
        self.cache = []

    def __repr__(self):
        return '<KBucket: {0} {1} {2}>'.format(self.k, self.bucket, self.cache)

    def __str__(self):
        return 'KBucket[{0}] ({1}/{3}) ({2}/{3})'.format(len(self), len(self.bucket), len(self.cache), self.k)

    def __contains__(self, item):
        return item in self.bucket or item in self.cache

    def __len__(self):
        return len(self.bucket) + len(self.cache)

    def __iter__(self):
        return itertools.chain(self.bucket, self.cache)

    @property
    def is_bucket_full(self):
        return len(self.bucket) >= self.k

    @property
    def is_cache_full(self):
        return len(self.cache) >= self.k

    def add(self, node):
        if node in self:
            self.remove(node)
        if self.is_bucket_full:
            if self.is_cache_full:
                self.cache.pop()
            self.cache.append(node)
        else:
            self.bucket.append(node)

    def remove(self, node):
        if node in self.bucket:
            self.bucket.remove(node)
        elif node in self.cache:
            self.cache.remove(node)
