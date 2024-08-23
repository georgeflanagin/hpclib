import unittest
from sloppytree import * 

class TestSloppyDict(unittest.TestCase):


    def setUp(self):
        # Sample dictionaries to use in tests
        self.long_dict = {
            'l1': {
                'l2': {
                    'l3a': {'k1': 'v1', 'k2': 'v2'},
                    'l3b': ['i1', 'i2', 'i3']
                },
                'k3': 'v3'
            },
            'l1_list': [{'l1i1': 'v4'}, {'l1i2': 'v5'}]
        }
        self.simple_dict = {
            'name': 'Alice',
            'age': 30,
            'city': 'Wonderland',
            'occupation': 'Adventurer'
        }
        self.empty_dict = {}

    def test_sloppy(self):
        sd = sloppy(self.long_dict)
        self.assertIsInstance(sd, SloppyDict)

    def test_deepsloppy(self):
        ds = deepsloppy(self.long_dict)
        self.assertEqual(ds.l1.l2.l3a.k1, 'v1')

# Test case for Sloppy Dict
    def test_getattr(self):
        sd2 = SloppyDict(self.long_dict)
        self.assertEqual(sd2.l1, self.long_dict['l1'])
        self.assertEqual(sd2.l1_list, self.long_dict['l1_list'])
        with self.assertRaises(SloppyException) as context:
            _ = sd2.non_existent_key
    
        self.assertIn("No element named non_existent_key", str(context.exception))


    def test_setattr(self):
        sd2 = SloppyDict(self.long_dict)
        sd2.hello = "world"
        self.assertEqual(sd2.hello, "world")

    def test_delattr(self):
        sd2 = SloppyDict(self.long_dict)
        sd2.hello = "world"
        del sd2.hello
        with self.assertRaises(SloppyException) as t:
            hasattr(sd2,'hello')
        self.assertIn('No element named hello', str(t.exception))

    def test_reorder_somekeys(self):
        sd3 = SloppyDict(self.simple_dict)
        desired_order = ['city', 'name']
        reordered_dict = sd3.reorder(desired_order)
        self.assertEqual(list(reordered_dict.keys())[:2], desired_order)
        with self.assertRaises(SloppyException) as t:
            o = ['hi','name']
            _ = sd3.reorder(o)
        self.assertIn('hi not found', str(t.exception))

    def test_reorder_selfassign(self):
        sd = SloppyDict(self.simple_dict)
        sd1 = sd.reorder(sd, self_assign=True)
        self.assertEqual(sd1, sd)

# Test cases for Sloppy Tree

    def test_st_getattr(self):
        sd = SloppyTree(self.simple_dict)
        self.assertEqual(sd.name, 'Alice')
        self.assertEqual(sd.gender, {})


    def test_st_setitem(self):
        sd = SloppyTree(self.simple_dict)
        sd.gender = 'F'
        self.assertEqual(sd.gender, 'F')

    def test_st_call(self):
        sd = SloppyTree(self.simple_dict)
        self.assertEqual(sd("name"), 'Alice') 
        with self.assertRaises(SloppyException) as t:
            _ = sd("name.pid")
        self.assertIn("k='pid' not found in sub-tree ptr='Alice'", str(t.exception))

    def test_st_setattr(self):
        sd = SloppyTree(self.simple_dict)
        sd[("gender", "sex")] = "Female"
        self.assertEqual(sd("gender.sex"), "Female")

    def test_st_delattr(self):
        sd = SloppyTree(self.simple_dict)
        del sd.name
        self.assertFalse(hasattr(type(sd), 'name'))

    def test_invert(self):
        sd = SloppyTree(self.long_dict)
        self.assertEqual(sd.__invert__(), 5)


    def test_iter(self):
        sd = SloppyTree(self.long_dict)
        #print([i for i in sd])

    def test_bool(self):
        sd = SloppyTree(self.long_dict)
        self.assertEqual(bool(sd), True)

        sd1 = SloppyTree(self.empty_dict)
        self.assertEqual(bool(sd1), False)

    def test_len(self):
        sd = SloppyTree(self.empty_dict)
        self.assertEqual(len(sd), 0)


    def test_missing(self):
        sd = SloppyTree(self.empty_dict)
        k = 'hello'
        self.assertNotIn(k, sd)
        self.assertIsInstance(sd[k], SloppyTree)
        self.assertIn(k, sd)
    
    def test_printable(self):
        sd = SloppyTree(self.long_dict)
        #print(sd.printable)

    def test_traverse(self):
        sd = SloppyTree(self.long_dict)
        #print([i for i in sd.traverse()]) 

    def test_as_tuples(self):
        sd = SloppyTree(self.long_dict)
        #print([i for i in sd.as_tuples()])                                            

    def test_tree_as_table(self):
        sd = SloppyTree(self.long_dict)
        #print(sd.__iter__())
        #print([i for i in sd.tree_as_table()])

if __name__ == '__main__':
    unittest.main()

