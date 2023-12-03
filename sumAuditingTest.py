from simulatableAuditing import SumAuditing, PrivacyLeakException
import unittest


class TestSumAuditing(unittest.TestCase):

    def setUp(self):
        self.auditor = SumAuditing([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])

    def test_no_privacy_leak(self):
        self.assertEqual(self.auditor.execute_query("1,2,3"), 6)
        self.assertEqual(self.auditor.execute_query("1,2,3,4,5"), 15)

    def test_duplicate_query(self):
        self.assertEqual(self.auditor.execute_query("1,2,3"), 6)
        self.assertEqual(self.auditor.execute_query("1,2,3"), 6)

    def test_privacy_leak(self):
        self.assertEqual(self.auditor.execute_query("1,2,3"), 6)
        with self.assertRaises(PrivacyLeakException):
            self.auditor.execute_query("1,2,3,4")

    def test_privacy_leak_single_query(self):
        with self.assertRaises(PrivacyLeakException):
            self.auditor.execute_query("1")

    def test_invalid_query(self):
        with self.assertRaises(ValueError):
            self.auditor.execute_query("1,2,3,11")

    def test_invalid_data(self):
        with self.assertRaises(ValueError):
            SumAuditing([1])


unittest.main()
