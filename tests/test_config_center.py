import unittest
import sys
import os

# Add the parent directory to the path so we can import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def merge_dict(dict1, dict2):
    """
    Merge two dictionaries recursively.
    This is a copy of the merge_dict function from utils.config_center.
    """
    for key in dict2:
        if key in dict1 and isinstance(dict1[key], dict) and isinstance(dict2[key], dict):
            merge_dict(dict1[key], dict2[key])
        else:
            dict1[key] = dict2[key]
    return dict1


class TestConfigCenter(unittest.TestCase):
    """Test cases for config center utility functions."""

    def test_merge_dict_basic(self):
        """Test basic dictionary merging."""
        dict1 = {'a': 1, 'b': 2}
        dict2 = {'c': 3, 'd': 4}
        
        result = merge_dict(dict1.copy(), dict2)
        expected = {'a': 1, 'b': 2, 'c': 3, 'd': 4}
        
        self.assertEqual(result, expected)

    def test_merge_dict_overwrite(self):
        """Test dictionary merging with overwriting values."""
        dict1 = {'a': 1, 'b': 2}
        dict2 = {'b': 3, 'c': 4}
        
        result = merge_dict(dict1.copy(), dict2)
        expected = {'a': 1, 'b': 3, 'c': 4}
        
        self.assertEqual(result, expected)

    def test_merge_dict_nested(self):
        """Test merging nested dictionaries."""
        dict1 = {
            'level1': {
                'a': 1,
                'b': 2,
                'level2': {
                    'x': 10,
                    'y': 20
                }
            }
        }
        dict2 = {
            'level1': {
                'b': 3,
                'c': 4,
                'level2': {
                    'y': 30,
                    'z': 40
                }
            }
        }
        
        result = merge_dict(dict1.copy(), dict2)
        expected = {
            'level1': {
                'a': 1,
                'b': 3,
                'c': 4,
                'level2': {
                    'x': 10,
                    'y': 30,
                    'z': 40
                }
            }
        }
        
        self.assertEqual(result, expected)

    def test_merge_dict_empty_dicts(self):
        """Test merging with empty dictionaries."""
        dict1 = {}
        dict2 = {'a': 1, 'b': 2}
        
        result = merge_dict(dict1.copy(), dict2)
        expected = {'a': 1, 'b': 2}
        
        self.assertEqual(result, expected)

    def test_merge_dict_empty_second(self):
        """Test merging with empty second dictionary."""
        dict1 = {'a': 1, 'b': 2}
        dict2 = {}
        
        result = merge_dict(dict1.copy(), dict2)
        expected = {'a': 1, 'b': 2}
        
        self.assertEqual(result, expected)

    def test_merge_dict_both_empty(self):
        """Test merging two empty dictionaries."""
        dict1 = {}
        dict2 = {}
        
        result = merge_dict(dict1.copy(), dict2)
        expected = {}
        
        self.assertEqual(result, expected)

    def test_merge_dict_mixed_types(self):
        """Test merging dictionaries with mixed value types."""
        dict1 = {
            'string': 'hello',
            'number': 42,
            'list': [1, 2, 3],
            'nested': {'a': 1}
        }
        dict2 = {
            'string': 'world',
            'boolean': True,
            'nested': {'b': 2}
        }
        
        result = merge_dict(dict1.copy(), dict2)
        expected = {
            'string': 'world',
            'number': 42,
            'list': [1, 2, 3],
            'boolean': True,
            'nested': {'a': 1, 'b': 2}
        }
        
        self.assertEqual(result, expected)

    def test_merge_dict_non_dict_overwrite(self):
        """Test that non-dict values overwrite dict values."""
        dict1 = {'key': {'nested': 'value'}}
        dict2 = {'key': 'simple_value'}
        
        result = merge_dict(dict1.copy(), dict2)
        expected = {'key': 'simple_value'}
        
        self.assertEqual(result, expected)

    def test_merge_dict_dict_overwrite_non_dict(self):
        """Test that dict values overwrite non-dict values."""
        dict1 = {'key': 'simple_value'}
        dict2 = {'key': {'nested': 'value'}}
        
        result = merge_dict(dict1.copy(), dict2)
        expected = {'key': {'nested': 'value'}}
        
        self.assertEqual(result, expected)

    def test_merge_dict_modifies_first_dict(self):
        """Test that merge_dict modifies the first dictionary in place."""
        dict1 = {'a': 1}
        dict2 = {'b': 2}
        
        original_dict1 = dict1.copy()
        result = merge_dict(dict1, dict2)
        
        # The result should be the same object as dict1
        self.assertIs(result, dict1)
        # dict1 should be modified
        self.assertNotEqual(dict1, original_dict1)
        self.assertEqual(dict1, {'a': 1, 'b': 2})


if __name__ == '__main__':
    unittest.main()