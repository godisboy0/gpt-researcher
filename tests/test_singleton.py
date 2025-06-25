import unittest
import sys
import os

# Add the parent directory to the path so we can import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.singleton import Singleton


class TestSingleton(unittest.TestCase):
    """Test cases for Singleton metaclass."""

    def setUp(self):
        """Clear singleton instances before each test."""
        Singleton._instances.clear()

    def test_singleton_single_instance(self):
        """Test that singleton creates only one instance."""
        
        class TestClass(metaclass=Singleton):
            def __init__(self, value=None):
                self.value = value

        instance1 = TestClass("first")
        instance2 = TestClass("second")
        
        # Both variables should reference the same instance
        self.assertIs(instance1, instance2)
        # The value should be from the first instantiation
        self.assertEqual(instance1.value, "first")
        self.assertEqual(instance2.value, "first")

    def test_singleton_different_classes(self):
        """Test that different classes have different singleton instances."""
        
        class TestClass1(metaclass=Singleton):
            def __init__(self, value=None):
                self.value = value

        class TestClass2(metaclass=Singleton):
            def __init__(self, value=None):
                self.value = value

        instance1 = TestClass1("class1")
        instance2 = TestClass2("class2")
        
        # Different classes should have different instances
        self.assertIsNot(instance1, instance2)
        self.assertEqual(instance1.value, "class1")
        self.assertEqual(instance2.value, "class2")

    def test_singleton_with_args_and_kwargs(self):
        """Test singleton with various arguments."""
        
        class TestClass(metaclass=Singleton):
            def __init__(self, arg1, arg2, kwarg1=None, kwarg2=None):
                self.arg1 = arg1
                self.arg2 = arg2
                self.kwarg1 = kwarg1
                self.kwarg2 = kwarg2

        instance1 = TestClass("a", "b", kwarg1="c", kwarg2="d")
        instance2 = TestClass("x", "y", kwarg1="z", kwarg2="w")
        
        # Should be the same instance
        self.assertIs(instance1, instance2)
        # Should retain values from first instantiation
        self.assertEqual(instance1.arg1, "a")
        self.assertEqual(instance1.arg2, "b")
        self.assertEqual(instance1.kwarg1, "c")
        self.assertEqual(instance1.kwarg2, "d")

    def test_singleton_inheritance(self):
        """Test singleton behavior with inheritance."""
        
        class BaseClass(metaclass=Singleton):
            def __init__(self, value=None):
                self.value = value

        class DerivedClass(BaseClass):
            def __init__(self, value=None, extra=None):
                super().__init__(value)
                self.extra = extra

        base_instance1 = BaseClass("base")
        base_instance2 = BaseClass("base2")
        derived_instance1 = DerivedClass("derived", "extra")
        derived_instance2 = DerivedClass("derived2", "extra2")
        
        # Base class instances should be the same
        self.assertIs(base_instance1, base_instance2)
        # Derived class instances should be the same
        self.assertIs(derived_instance1, derived_instance2)
        # Base and derived should be different
        self.assertIsNot(base_instance1, derived_instance1)

    def test_singleton_no_args(self):
        """Test singleton with no constructor arguments."""
        
        class TestClass(metaclass=Singleton):
            def __init__(self):
                self.created = True

        instance1 = TestClass()
        instance2 = TestClass()
        
        self.assertIs(instance1, instance2)
        self.assertTrue(instance1.created)

    def test_singleton_instances_dict(self):
        """Test that singleton instances are stored correctly."""
        
        class TestClass(metaclass=Singleton):
            pass

        # Initially no instances
        initial_count = len(Singleton._instances)
        
        instance1 = TestClass()
        # Should have one more instance
        self.assertEqual(len(Singleton._instances), initial_count + 1)
        
        instance2 = TestClass()
        # Should still have the same number of instances
        self.assertEqual(len(Singleton._instances), initial_count + 1)
        
        # The class should be a key in the instances dict
        self.assertIn(TestClass, Singleton._instances)
        self.assertIs(Singleton._instances[TestClass], instance1)


if __name__ == '__main__':
    unittest.main()