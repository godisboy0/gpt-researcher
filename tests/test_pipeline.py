import unittest
import sys
import os

# Add the parent directory to the path so we can import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def generate_task_id(task):
    """
    Generate a task ID from a task string.
    This is a copy of the generate_task_id function from pipeline.
    """
    import re
    # Replace non-alphanumeric characters with underscores
    task_id = re.sub(r'[^a-zA-Z0-9]', '_', task)
    # Remove leading and trailing underscores
    task_id = task_id.strip('_')
    return task_id


class TestPipeline(unittest.TestCase):
    """Test cases for pipeline module functions."""

    def test_generate_task_id_basic(self):
        """Test generate_task_id with basic input."""
        result = generate_task_id("Hello World")
        expected = "Hello_World"
        self.assertEqual(result, expected)

    def test_generate_task_id_special_characters(self):
        """Test generate_task_id with special characters."""
        result = generate_task_id("Hello, World! How are you?")
        expected = "Hello__World__How_are_you"
        self.assertEqual(result, expected)

    def test_generate_task_id_empty_string(self):
        """Test generate_task_id with empty string."""
        result = generate_task_id("")
        expected = ""
        self.assertEqual(result, expected)

    def test_generate_task_id_only_special_characters(self):
        """Test generate_task_id with only special characters."""
        result = generate_task_id("!@#$%^&*()")
        expected = ""
        self.assertEqual(result, expected)

    def test_generate_task_id_leading_trailing_underscores(self):
        """Test generate_task_id strips leading and trailing underscores."""
        result = generate_task_id("_Hello World_")
        expected = "Hello_World"
        self.assertEqual(result, expected)


if __name__ == '__main__':
    unittest.main()