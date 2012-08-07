__author__ = 'ahawker'

from kettle.tests.structures import KettleTest
from kettle.tests.dht.kademlia.test_nodes import default_node
from kettle.dht.kademlia.kbucket import KBucket, KBucketOverflow

class TestKBucket(KettleTest):

    def setUp(self):
        self.bucket = KBucket()

    def test_default_attributes(self):
        self.assertEqual(self.bucket.k, 20)

    def test_attribute_assignment(self):
        b = KBucket(1)
        self.assertEqual(b.k, 1)

    def test_repr(self):
        self.assertIsNotNone(repr(self.bucket))
        self.assertTrue(len(repr(self.bucket)) > 0)

    def test_str(self):
        self.assertIsNotNone(repr(self.bucket))
        self.assertTrue(len(repr(self.bucket)) > 0)

    def test_contains(self):
        self.assertFalse(default_node in self.bucket)
        self.bucket.add(default_node)
        self.assertTrue(default_node in self.bucket)

    def test_len(self):
        self.assertEqual(len(self.bucket), 0)
        self.bucket.add(default_node)
        self.assertEqual(len(self.bucket), 1)

    def test_iter(self):
        self.assertItemsEqual(self.bucket, [])
        self.bucket.add(default_node)
        self.assertItemsEqual(self.bucket, [default_node])

    def test_add(self):
        self.bucket.add(default_node)
        self.assertEqual(len(self.bucket), 1)
        self.assertTrue(default_node in self.bucket)

    def test_add_overflow(self):
        b = KBucket(1)
        b.add(default_node)
        self.assertRaises(KBucketOverflow, b.add, default_node)

    def test_add_existing_item(self):
        self.bucket.add(default_node)
        self.bucket.add(default_node)
        self.assertEqual(len(self.bucket), 1)
        self.assertTrue(default_node in self.bucket)

    def test_remove(self):
        self.bucket.add(default_node)
        self.assertEqual(len(self.bucket), 1)
        self.assertTrue(default_node in self.bucket)
        self.bucket.remove(default_node)
        self.assertEqual(len(self.bucket), 0)
        self.assertFalse(default_node in self.bucket)

    def test_is_full(self):
        b = KBucket(1)
        self.assertFalse(b.is_full)
        b.add(default_node)
        self.assertTrue(b.is_full)

