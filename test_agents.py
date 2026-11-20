import unittest

import agents


class FuzzyTests(unittest.TestCase):
    def test_higher_urgency_gives_higher_priority(self):
        low = agents.priority(1, 50, 0)
        mid = agents.priority(2, 50, 0)
        high = agents.priority(3, 50, 0)
        self.assertLess(low, mid)
        self.assertLess(mid, high)

    def test_more_people_and_longer_wait_raise_priority(self):
        self.assertLess(agents.priority(3, 10, 0), agents.priority(3, 100, 0))
        self.assertLess(agents.priority(1, 50, 0), agents.priority(1, 50, 5))

    def test_priority_stays_between_0_and_1(self):
        for urgency in (1, 2, 3):
            for people in (10, 55, 100):
                for wait in (0, 2, 5, 9):
                    self.assertTrue(0 <= agents.priority(urgency, people, wait) <= 1)

    def test_membership_shapes(self):
        self.assertEqual(agents.grade(0)["low"], 1.0)
        self.assertEqual(agents.grade(0.5)["medium"], 1.0)
        self.assertEqual(agents.grade(1)["high"], 1.0)
        self.assertAlmostEqual(agents.grade(0.3)["low"], 0.5)


if __name__ == "__main__":
    unittest.main()
