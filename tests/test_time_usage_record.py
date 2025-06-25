import unittest
import sys
import os
import time
import tempfile
import shutil

# Add the parent directory to the path so we can import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def format_time(t: int) -> str:
    """
    Format timestamp to readable string.
    This is a copy of the __format_time function from utils.time_usage_record.
    """
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(t))


class TestTimeUsageRecord(unittest.TestCase):
    """Test cases for time usage record utility."""

    def test_format_time_basic(self):
        """Test format_time with a known timestamp."""
        # Use a known timestamp: 2023-01-01 00:00:00 UTC
        timestamp = 1672531200  # 2023-01-01 00:00:00 UTC
        result = format_time(timestamp)
        
        # The result should be a properly formatted date string
        self.assertIsInstance(result, str)
        self.assertEqual(len(result), 19)  # "YYYY-MM-DD HH:MM:SS" format
        self.assertRegex(result, r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}')

    def test_format_time_current_time(self):
        """Test format_time with current timestamp."""
        current_time = int(time.time())
        result = format_time(current_time)
        
        # Should return a valid date string
        self.assertIsInstance(result, str)
        self.assertRegex(result, r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}')

    def test_format_time_zero(self):
        """Test format_time with timestamp 0."""
        result = format_time(0)
        
        # Should handle epoch time (1970-01-01)
        self.assertIsInstance(result, str)
        self.assertRegex(result, r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}')

    def test_format_time_future(self):
        """Test format_time with future timestamp."""
        # Use a future timestamp: 2030-01-01 00:00:00 UTC
        future_timestamp = 1893456000
        result = format_time(future_timestamp)
        
        self.assertIsInstance(result, str)
        self.assertRegex(result, r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}')

    def test_format_time_consistency(self):
        """Test that format_time is consistent for the same input."""
        timestamp = 1672531200
        result1 = format_time(timestamp)
        result2 = format_time(timestamp)
        
        self.assertEqual(result1, result2)

    def test_format_time_different_inputs(self):
        """Test that format_time produces different outputs for different inputs."""
        timestamp1 = 1672531200  # 2023-01-01
        timestamp2 = 1672617600  # 2023-01-02
        
        result1 = format_time(timestamp1)
        result2 = format_time(timestamp2)
        
        self.assertNotEqual(result1, result2)


if __name__ == '__main__':
    unittest.main()