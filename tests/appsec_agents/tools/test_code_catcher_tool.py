import unittest
from unittest.mock import patch, MagicMock
from src.appsec_agents.tools.code_catcher_tool import CodePatternMatcherTool


class TestCodePatternMatcherTool(unittest.TestCase):

    def setUp(self):
        self.tool = CodePatternMatcherTool()

    @patch('subprocess.run')
    def test_run_success(self, mock_subprocess_run):
        mock_subprocess_run.return_value = MagicMock(
            returncode=0, stdout='Match found', stderr='')
        local_path = '/path/to/repo'
        pattern = 'regex_pattern'
        result = self.tool._run(local_path, pattern)
        self.assertEqual(
            result, f"Pattern matching completed successfully:\nMatch found")

    @patch('subprocess.run')
    def test_run_failure(self, mock_subprocess_run):
        mock_subprocess_run.return_value = MagicMock(
            returncode=1, stdout='', stderr='Error message')
        local_path = '/path/to/repo'
        pattern = 'regex_pattern'
        result = self.tool._run(local_path, pattern)
        self.assertEqual(result, f"No matches found for the pattern '{
                         pattern}' or an error occurred:\nError message")

    @patch('subprocess.run')
    def test_run_exception(self, mock_subprocess_run):
        mock_subprocess_run.side_effect = Exception('Mocked exception')
        local_path = '/path/to/repo'
        pattern = 'regex_pattern'
        result = self.tool._run(local_path, pattern)
        self.assertEqual(
            result, "Error running pattern matcher: Mocked exception")


if __name__ == '__main__':
    unittest.main()
