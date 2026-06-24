import unittest

from book_service import (
    build_distribution,
    count_words,
    extract_first_chapter,
    parse_metadata,
    round_down_to_ten,
    split_paragraphs,
)


SAMPLE = """Title: Example Book
Author: Jane Doe

CHAPTER I.
The Beginning

This is a first paragraph with seven simple words.

A second paragraph appears here.

CHAPTER II.
The Next Part
"""


class BookServiceTests(unittest.TestCase):
    def test_metadata(self) -> None:
        self.assertEqual(parse_metadata(SAMPLE), ("Example Book", "Jane Doe"))

    def test_first_chapter_and_paragraphs(self) -> None:
        chapter = extract_first_chapter(SAMPLE)
        paragraphs = split_paragraphs(chapter)
        self.assertEqual(len(paragraphs), 2)
        self.assertIn("first paragraph", chapter)
        self.assertNotIn("CHAPTER II", chapter)

    def test_count_and_distribution(self) -> None:
        self.assertEqual(count_words("Alice's very small test."), 4)
        self.assertEqual(round_down_to_ten(129), 120)
        self.assertEqual(build_distribution([9, 11, 18, 21]), {0: 1, 10: 2, 20: 1})


if __name__ == "__main__":
    unittest.main()


class LocalBackupTests(unittest.TestCase):
    def test_backup_book_contains_first_chapter(self) -> None:
        from config import BACKUP_BOOK_TEXT_PATH

        text = BACKUP_BOOK_TEXT_PATH.read_text(encoding="utf-8-sig")
        chapter = extract_first_chapter(text)
        paragraphs = split_paragraphs(chapter)
        self.assertGreater(len(paragraphs), 5)
        self.assertIn("Alice", chapter)
