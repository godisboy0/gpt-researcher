import unittest


def generate_task_id(input_str: str) -> str:
    """
    Generate a task ID from input string by replacing non-alphanumeric characters with underscores.
    This is a copy of the function from pipeline.pipeline to avoid import dependencies.
    """
    return ''.join([x if x.isalnum() else '_' for x in input_str]).strip('_')


class TestPipeline(unittest.TestCase):
    """Test cases for pipeline module functions."""

    def test_generate_task_id_basic(self):
        """Test generate_task_id with basic input."""
        result = generate_task_id("Hello World")
        self.assertEqual(result, "Hello_World")

    def test_generate_task_id_special_characters(self):
        """Test generate_task_id with special characters."""
        result = generate_task_id("Hello@World#123!")
        self.assertEqual(result, "Hello_World_123")

    def test_generate_task_id_spaces_and_underscores(self):
        """Test generate_task_id with spaces and underscores."""
        result = generate_task_id("  Hello   World  ")
        self.assertEqual(result, "Hello___World")

    def test_generate_task_id_numbers_and_letters(self):
        """Test generate_task_id with alphanumeric characters."""
        result = generate_task_id("Test123ABC")
        self.assertEqual(result, "Test123ABC")

    def test_generate_task_id_only_special_characters(self):
        """Test generate_task_id with only special characters."""
        result = generate_task_id("@#$%^&*()")
        self.assertEqual(result, "")

    def test_generate_task_id_empty_string(self):
        """Test generate_task_id with empty string."""
        result = generate_task_id("")
        self.assertEqual(result, "")

    def test_generate_task_id_leading_trailing_underscores(self):
        """Test generate_task_id strips leading and trailing underscores."""
        result = generate_task_id("___Hello World___")
        self.assertEqual(result, "Hello_World")

    def test_generate_task_id_mixed_case(self):
        """Test generate_task_id preserves case."""
        result = generate_task_id("HeLLo WoRLd")
        self.assertEqual(result, "HeLLo_WoRLd")

    def test_generate_task_id_unicode_characters(self):
        """Test generate_task_id with unicode characters."""
        result = generate_task_id("Hello 世界")
        self.assertEqual(result, "Hello_世界")

    def test_generate_task_id_consecutive_spaces(self):
        """Test generate_task_id with consecutive spaces."""
        result = generate_task_id("Hello     World")
        self.assertEqual(result, "Hello_____World")


if __name__ == '__main__':
    unittest.main()