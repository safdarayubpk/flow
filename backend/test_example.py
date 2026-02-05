import unittest

class TestExample(unittest.TestCase):
    """
    Example test class demonstrating basic test structure
    """

    def test_basic_assertion(self):
        """Test a basic assertion"""
        self.assertEqual(2 + 2, 4)

    def test_string_operations(self):
        """Test string operations"""
        text = "hello world"
        self.assertIn("world", text)
        self.assertTrue(text.startswith("hello"))

    def test_list_operations(self):
        """Test list operations"""
        my_list = [1, 2, 3, 4, 5]
        self.assertEqual(len(my_list), 5)
        self.assertIn(3, my_list)

if __name__ == '__main__':
    unittest.main()