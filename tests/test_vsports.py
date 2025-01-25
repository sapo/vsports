import unittest
from vsports.vsports import VsportsAPI

class TestVsportsAPI(unittest.TestCase):
    
    def setUp(self):
        self.api_key = "test_api_key"
        self.vsports = VsportsAPI(self.api_key)

    def test_events_by_date(self):
        result = self.vsports.events_by_date("2025-01-24", usecache=False)
        self.assertIsNotNone(result)
        self.assertIsInstance(result, list)

    def test_teams_by_tournament(self):
        result = self.vsports.teams_by_tournament(118, usecache=False)
        self.assertIsNotNone(result)
        self.assertIsInstance(result, list)

if __name__ == '__main__':
    unittest.main()
