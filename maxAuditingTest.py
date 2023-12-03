import unittest
from simulatableAuditing import MaxAuditing, PrivacyLeakException


class MaxAuditingTest(unittest.TestCase):
    def test_no_privacy_leak(self):
        auditor = MaxAuditing([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        self.assertEqual(auditor.execute_query("1,2,3"), 3)
        self.assertEqual(auditor.execute_query("1,2,3,4,5"), 5)

        auditor = MaxAuditing([1, 2, 10, 4, 8])
        self.assertEqual(auditor.execute_query("1,2,3,4,5"), 10)
        self.assertEqual(auditor.execute_query("1,2,3"), 10)
        self.assertEqual(auditor.execute_query("3,4"), 10)

    def test_duplicate_query(self):
        auditor = MaxAuditing([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        self.assertEqual(auditor.execute_query("1,2,3"), 3)
        self.assertEqual(auditor.execute_query("1,2,3"), 3)

    def test_privacy_leak(self):
        auditor = MaxAuditing([1, 2, 8, 4, 10])
        self.assertEqual(auditor.execute_query("1,2,3,4,5"), 10)
        self.assertEqual(auditor.execute_query("1,2,3"), 8)
        with self.assertRaises(PrivacyLeakException):
            auditor.execute_query("3,4")

    def test_privacy_leak_single_query(self):
        auditor = MaxAuditing([1, 2, 8, 4, 10])
        with self.assertRaises(PrivacyLeakException):
            auditor.execute_query("1")

    def test_invalid_query(self):
        auditor = MaxAuditing([1, 2, 8, 4, 10])
        with self.assertRaises(ValueError):
            auditor.execute_query("1,2,3,11")

    def test_invalid_data(self):
        with self.assertRaises(ValueError):
            MaxAuditing([1])
            
    def test_duplicate_dataset(self):
        with self.assertRaises(ValueError):
            MaxAuditing([1, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10])


unittest.main()
