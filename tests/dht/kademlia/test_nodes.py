__author__ = 'ahawker'

from tests.structures import KettleTest
from kettle.dht.kademlia.nodes import Node

default_address = '127.0.0.1'
default_port = 9995
default_id = 0

class TestNode(KettleTest):

    def setUp(self):
        self.node = Node(default_address, default_port, default_id)

    def test_attribute_assignment(self):
        self.assertEquals(self.node.address, default_address)
        self.assertEquals(self.node.port, default_port)
        self.assertEquals(self.node, default_id)

    def test_id_generation(self):
        n = Node(default_address, default_port)
        self.assertTrue(n > 0)
        self.assertEqual(len(str(n.nid)), 20)

    def test_repr(self):
        self.assertIsNotNone(repr(self.node))
        self.assertTrue(len(repr(self.node)) > 0)

    def test_str(self):
        self.assertIsNotNone(str(self.node))
        self.assertTrue(len(str(self.node)) > 0)

    def test_less_than(self):
        n = Node(default_address, default_port, 1)
        self.assertLess(self.node, n)

    def test_less_than_or_equal(self):
        n = Node(default_address, default_port, default_id)
        self.assertLessEqual(self.node, n)

    def test_greater_than(self):
        n = Node(default_address, default_port, -1)
        self.assertGreater(self.node, n)

    def test_greater_than_or_equal(self):
        n = Node(default_address, default_port, default_id)
        self.assertGreaterEqual(self.node, n)

    def test_equal(self):
        n = Node(default_address, default_port, default_id)
        self.assertEqual(self.node, n)
        self.assertTrue(self.node == n)

    def test_not_equal(self):
        n = Node(default_address, default_port, 1)
        self.assertNotEqual(self.node, n)
        self.assertTrue(self.node != n)

    def test_compare(self):
        n = Node(default_address, default_port, 1)
        self.assertEqual(cmp(self.node, n), -1)
        self.assertEqual(cmp(n, self.node), 1)
        self.assertEqual(cmp(self.node, self.node), 0)
        self.assertEqual(cmp(n, n), 0)

    def test_exclusive_or(self):
        n = Node(default_address, default_port, 1)
        self.assertEqual(self.node ^ self.node, self.node)
        self.assertEqual(self.node ^ n, n)
        self.assertEqual(n ^ 2, 3)
        self.assertEqual(n ^ 3, 2)

    def test_hash(self):
        n = Node(default_address, default_port, 1)
        self.assertEqual(hash(self.node), self.node)
        self.assertEqual(hash(n), n)

    def test_distance(self):
        n = Node(default_address, default_port, 1)
        self.assertEqual(self.node ^ self.node, self.node.distance(self.node))
        self.assertEqual(n ^ n, n.distance(n))
        self.assertEqual(self.node ^ n, self.node.distance(n))
        self.assertEqual(n ^ 2, n.distance(2))
        self.assertEqual(n ^ 3, n.distance(3))

    def test_to_dict(self):
        d = self.node.to_dict()
        keys = ['address', 'port', 'id']
        values = [default_address, default_port, default_id]
        self.assertEqual(len(set(keys) - set(d.keys())), 0)
        self.assertEqual(len(set(values) - set(d.values())), 0)

    def test_to_json(self):
        import json
        j = self.node.to_json()
        keys = ['address', 'port', 'id']
        values = [default_address, default_port, default_id]
        self.assertEqual(len(set(keys) - set(json.loads(str(j)).keys())), 0)
        self.assertEqual(len(set(values) - set(json.loads(str(j)).values())), 0)

