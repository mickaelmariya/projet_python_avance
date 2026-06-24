import tempfile
import unittest
from pathlib import Path

from database import Database
from models import TodoRecord


class DatabaseTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.database = Database(Path(self.temp_dir.name) / "test.db")

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_replace_and_aggregate(self) -> None:
        records = [
            TodoRecord(1, 1, "abc", "Terminé", 3),
            TodoRecord(2, 1, "abcdefg", "En attente", 7),
        ]
        self.assertEqual(self.database.replace_all(records), 2)
        stats = self.database.aggregate()
        self.assertEqual(stats["total"], 2)
        self.assertEqual(stats["completed"], 1)
        self.assertEqual(stats["pending"], 1)
        self.assertEqual(stats["average_length"], 5.0)

    def test_append_ignores_duplicates(self) -> None:
        record = TodoRecord(1, 1, "abc", "Terminé", 3)
        self.database.replace_all([record])
        self.assertEqual(self.database.append_new([record]), 0)


if __name__ == "__main__":
    unittest.main()
