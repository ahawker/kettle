__author__ = 'ahawker'

class KBucket(object):
    def __init__(self, k=20, range=(0, 2**160)):
        super(KBucket, self).__init__()
        self.k = k
        self.min, self.max = range
        self.items = []

    def __repr__(self):
        return '<KBucket [{0}, {1}] {2} {3}>'.format(self.min, self.max, self.k, len(self))

    def __str__(self):
        return 'Range: [{0}, {1}] Size: {{{2}}} Items: {{{3}}}'.format(self.min, self.max, self.k, len(self))

    def __contains__(self, item):
        return item in self.items

    def __len__(self):
        return len(self.items)

    def __iter__(self):
        return iter(self.items)

    def add(self, node):
        if self.is_full:
            raise KBucketOverflow('Bucket is full with {0} items.'.format(len(self)))
        if node in self: #already in list, remove and add append (tail)
            self.items.remove(node)
        self.items.append(node)

    def remove(self, node):
        if node in self:
            self.items.remove(node)

    @property
    def is_full(self):
        return len(self) >= self.k

    def key_in_range(self, value):
        return self.min <= value <= self.max

    def can_split(self, value):
        return self.key_in_range(value)

    @classmethod
    def split(cls, b1, b2):
        pass


class KBucketOverflow(Exception):
    pass

