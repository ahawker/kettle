__author__  = 'Andrew Hawker <andrew.r.hawker@gmail.com>'

from tests.fixtures import default_node
from kettle.kettle import KBucket
import unittest

class TestKBucket(unittest.TestCase):

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

    def test_contains_cache(self):
        b = KBucket(1)
        b.add(None)
        b.add(default_node)
        self.assertTrue(default_node in b)

    def test_len(self):
        self.assertEqual(len(self.bucket), 0)
        self.bucket.add(default_node)
        self.assertEqual(len(self.bucket), 1)

    def test_len_cache(self):
        b = KBucket(1)
        b.add(None)
        b.add(default_node)
        self.assertEqual(len(b), 2)

    def test_iter(self):
        self.assertItemsEqual(self.bucket, [])
        self.bucket.add(default_node)
        self.assertItemsEqual(self.bucket, [default_node])

    def test_iter_cache(self):
        b = KBucket(1)
        b.add(None)
        b.add(default_node)
        self.assertItemsEqual(b, [None, default_node])

    def test_add(self):
        self.bucket.add(default_node)
        self.assertEqual(len(self.bucket), 1)
        self.assertTrue(default_node in self.bucket)

    def test_add_overflow(self):
        b = KBucket(1)
        b.add(None)
        b.add(default_node)
        self.assertEquals(len(b), 2)
        self.assertTrue(b.is_bucket_full)
        self.assertEquals(len(b.cache), 1)
        self.assertEquals(len(b.bucket), 1)

    def test_add_cache_overflow(self):
        b = KBucket(1)
        b.add(None)
        b.add(default_node)
        b.add(default_node)
        self.assertEquals(len(b), 2)
        self.assertTrue(b.is_cache_full)
        self.assertEquals(len(b.cache), 1)
        self.assertEquals(len(b.bucket), 1)

    def test_add_existing_item(self):
        self.bucket.add(default_node)
        self.bucket.add(default_node)
        self.assertEqual(len(self.bucket), 1)
        self.assertTrue(default_node in self.bucket)

    def test_add_cache_existing_item(self):
        b = KBucket(1)
        b.add(None)
        b.add(default_node)
        b.add(default_node)
        self.assertEqual(len(b), 2)

    def test_remove(self):
        self.bucket.add(default_node)
        self.assertEqual(len(self.bucket), 1)
        self.assertTrue(default_node in self.bucket)
        self.bucket.remove(default_node)
        self.assertEqual(len(self.bucket), 0)
        self.assertFalse(default_node in self.bucket)

    def test_cache_remove(self):
        b = KBucket(1)
        b.add(None)
        b.add(default_node)
        self.assertEqual(len(b), 2)
        b.remove(default_node)
        self.assertEqual(len(b), 1)

    def test_is_full(self):
        b = KBucket(1)
        self.assertFalse(b.is_bucket_full)
        b.add(default_node)
        self.assertTrue(b.is_bucket_full)

    def test_is_cache_full(self):
        b = KBucket(1)
        b.add(None)
        b.add(default_node)
        self.assertTrue(b.is_cache_full)

if __name__ == '__main__':
    unittest.main()