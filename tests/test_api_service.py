import unittest

from api_service import build_french_task_name


class ApiServiceTests(unittest.TestCase):
    def test_french_names_are_stable_and_unique(self) -> None:
        names = [build_french_task_name(identifier) for identifier in range(1, 201)]
        self.assertEqual(len(names), 200)
        self.assertEqual(len(set(names)), 200)
        self.assertTrue(names[0].startswith("Préparer"))
        self.assertIn("équipe", names[0])


if __name__ == "__main__":
    unittest.main()
