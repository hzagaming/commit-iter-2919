import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from iter_commit import version_for  # noqa: E402


class VersionTest(unittest.TestCase):
    def test_start(self):
        self.assertEqual(version_for(2919), "0.0.2919")

    def test_no_carry_below_10000(self):
        self.assertEqual(version_for(9999), "0.0.9999")

    def test_carry_to_minor(self):
        self.assertEqual(version_for(10000), "0.1.0000")
        self.assertEqual(version_for(10001), "0.1.0001")

    def test_carry_to_major(self):
        self.assertEqual(version_for(100_000_000), "1.0.0000")
        self.assertEqual(version_for(100_010_000), "1.1.0000")

    def test_negative_rejected(self):
        with self.assertRaises(ValueError):
            version_for(-1)


if __name__ == "__main__":
    unittest.main()
