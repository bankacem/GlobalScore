import importlib.util
from datetime import datetime, timezone
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("update_data", ROOT / "scripts" / "update_data.py")
update_data = importlib.util.module_from_spec(spec)
spec.loader.exec_module(update_data)


class MatchMappingTests(unittest.TestCase):
    def test_unplayed_match_does_not_become_zero_zero(self):
        event = {
            "idEvent": "future-1",
            "strSport": "Soccer",
            "strStatus": "Not Started",
            "strTimestamp": "2026-09-10T18:00:00Z",
            "strHomeTeam": "Home",
            "strAwayTeam": "Away",
            "intHomeScore": None,
            "intAwayScore": None,
        }
        match = update_data.event_to_match(
            event,
            "Test League",
            "دوري الاختبار",
            datetime(2026, 9, 10, 8, tzinfo=timezone.utc),
        )
        self.assertEqual(match["score"], "— - —")
        self.assertEqual(match["status"], "Scheduled")

    def test_finished_zero_zero_is_preserved(self):
        event = {
            "idEvent": "finished-1",
            "strSport": "Soccer",
            "strStatus": "Finished",
            "strTimestamp": "2026-09-09T18:00:00Z",
            "strHomeTeam": "Home",
            "strAwayTeam": "Away",
            "intHomeScore": 0,
            "intAwayScore": 0,
        }
        match = update_data.event_to_match(
            event,
            "Test League",
            "دوري الاختبار",
            datetime(2026, 9, 10, 8, tzinfo=timezone.utc),
        )
        self.assertEqual(match["score"], "0 - 0")
        self.assertEqual(match["status"], "FT")


if __name__ == "__main__":
    unittest.main()
