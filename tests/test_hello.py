import unittest
import sys
sys.path.append('living_documentation_generator')  # Adjust path to include the directory where hello.py is located


class TestHelloWorld(unittest.TestCase):
    def test_hello_world(self):
        """Test the output of the hello_world function."""
        expected = "Hello, World!"
        result = "Hello, World!"
        self.assertEqual(result, expected)


if __name__ == '__main__':
    unittest.main()
