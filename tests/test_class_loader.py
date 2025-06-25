import unittest
import sys
import os
import tempfile
import importlib.util

# Add the parent directory to the path so we can import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.class_loader import load_class_from_module


class TestClassLoader(unittest.TestCase):
    """Test cases for class loader utility."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary module for testing
        self.temp_dir = tempfile.mkdtemp()
        sys.path.insert(0, self.temp_dir)

    def tearDown(self):
        """Clean up test fixtures."""
        # Remove temporary directory from path
        if self.temp_dir in sys.path:
            sys.path.remove(self.temp_dir)

    def test_load_class_from_module_basic(self):
        """Test loading classes from a module."""
        # Create a temporary module file
        module_content = '''
class BaseClass:
    pass

class DerivedClass1(BaseClass):
    pass

class DerivedClass2(BaseClass):
    pass

class UnrelatedClass:
    pass
'''
        module_path = os.path.join(self.temp_dir, 'test_module.py')
        with open(module_path, 'w') as f:
            f.write(module_content)

        # Import the module dynamically
        spec = importlib.util.spec_from_file_location("test_module", module_path)
        test_module = importlib.util.module_from_spec(spec)
        sys.modules["test_module"] = test_module
        spec.loader.exec_module(test_module)

        # Test loading classes
        base_class = test_module.BaseClass
        classes = load_class_from_module("test_module", base_class)

        # Should find 2 derived classes
        self.assertEqual(len(classes), 2)
        
        # Check that the correct classes are loaded
        class_names = [cls.__name__ for cls in classes]
        self.assertIn("DerivedClass1", class_names)
        self.assertIn("DerivedClass2", class_names)
        self.assertNotIn("BaseClass", class_names)
        self.assertNotIn("UnrelatedClass", class_names)

    def test_load_class_from_module_no_subclasses(self):
        """Test loading from module with no subclasses."""
        module_content = '''
class BaseClass:
    pass

class UnrelatedClass:
    pass
'''
        module_path = os.path.join(self.temp_dir, 'test_module2.py')
        with open(module_path, 'w') as f:
            f.write(module_content)

        # Import the module dynamically
        spec = importlib.util.spec_from_file_location("test_module2", module_path)
        test_module = importlib.util.module_from_spec(spec)
        sys.modules["test_module2"] = test_module
        spec.loader.exec_module(test_module)

        # Test loading classes
        base_class = test_module.BaseClass
        classes = load_class_from_module("test_module2", base_class)

        # Should find no derived classes
        self.assertEqual(len(classes), 0)

    def test_load_class_from_module_inheritance_chain(self):
        """Test loading classes with inheritance chain."""
        module_content = '''
class BaseClass:
    pass

class MiddleClass(BaseClass):
    pass

class DerivedClass(MiddleClass):
    pass

class AnotherDerived(BaseClass):
    pass
'''
        module_path = os.path.join(self.temp_dir, 'test_module3.py')
        with open(module_path, 'w') as f:
            f.write(module_content)

        # Import the module dynamically
        spec = importlib.util.spec_from_file_location("test_module3", module_path)
        test_module = importlib.util.module_from_spec(spec)
        sys.modules["test_module3"] = test_module
        spec.loader.exec_module(test_module)

        # Test loading classes
        base_class = test_module.BaseClass
        classes = load_class_from_module("test_module3", base_class)

        # Should find all classes that inherit from BaseClass
        self.assertEqual(len(classes), 3)
        
        class_names = [cls.__name__ for cls in classes]
        self.assertIn("MiddleClass", class_names)
        self.assertIn("DerivedClass", class_names)
        self.assertIn("AnotherDerived", class_names)
        self.assertNotIn("BaseClass", class_names)

    def test_load_class_from_existing_module(self):
        """Test loading classes from an existing module in the project."""
        # Test with the actual utils module
        from utils import singleton
        
        # Create a base class for testing
        class TestBase:
            pass
        
        # Since singleton.py doesn't have subclasses of our TestBase,
        # this should return an empty list
        classes = load_class_from_module("utils.singleton", TestBase)
        self.assertEqual(len(classes), 0)

    def test_load_class_from_nonexistent_module(self):
        """Test loading from non-existent module raises ImportError."""
        class TestBase:
            pass
            
        with self.assertRaises(ModuleNotFoundError):
            load_class_from_module("nonexistent_module", TestBase)


if __name__ == '__main__':
    unittest.main()