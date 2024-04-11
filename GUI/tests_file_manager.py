import unittest
from file_manager import FileManager  # Ensure this matches your module and class names

class TestFileManager(unittest.TestCase):
    def setUp(self):
        self.fm = FileManager()

    def test_load_file(self):
        result = self.fm.load_file('test_file.txt', 'test_data')
        self.assertTrue(result)
        self.assertIn('test_file.txt', self.fm.loaded_files)

    def test_unload_file(self):
        self.fm.load_file('test_file.txt', 'test_data')
        result = self.fm.unload_file('test_file.txt')
        self.assertTrue(result)
        self.assertNotIn('test_file.txt', self.fm.loaded_files)

    def test_list_files(self):
        self.fm.load_file('test_file.txt', 'test_data')
        result = self.fm.list_files()
        self.assertIsInstance(result, list)
        self.assertIn('test_file.txt', result)

if __name__ == '__main__':
    unittest.main()
