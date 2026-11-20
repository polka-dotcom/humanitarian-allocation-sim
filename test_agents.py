
import unittest
 
import agents
 
 
def make_req(i, item, qty, urgency, people):
    return {"id": i, "zone": "A", "item": item, "qty": qty, "urgency": urgency,
            "people": people, "arrival": 0, "given": 0, "filled_round": None}
 
 
def make_state(requests, medicine):
    return {"requests": requests, "round": 0, "seed": 0,
            "stock": {"medicine": medicine, "shelter": 0, "nutrition": 0}}
 
 
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
 
 
class FsmTests(unittest.TestCase):
    def test_mode_follows_stock_ratio(self):
        r = make_req(0, "medicine", 4, 3, 50)
        self.assertEqual(agents.mode(make_state([r], 4)), "normal")
        self.assertEqual(agents.mode(make_state([r], 2)), "scarce")
        self.assertEqual(agents.mode(make_state([r], 1)), "critical")
 
    def test_scarce_mode_caps_each_fill_at_half_the_request(self):
        a = make_req(0, "medicine", 4, 3, 50)
        b = make_req(1, "medicine", 4, 2, 50)
        plan = agents.fuzzy_fsm(make_state([a, b], 5))
        self.assertEqual([units for _, units, _ in plan], [2, 2])
 
    def test_critical_mode_skips_low_priority_requests(self):
        urgent = make_req(0, "medicine", 4, 3, 100)
        minor = make_req(1, "medicine", 4, 1, 10)
        plan = agents.fuzzy_fsm(make_state([urgent, minor], 2))
        units = {r["id"]: u for r, u, _ in plan}
        self.assertEqual(units[0], 4)
        self.assertEqual(units[1], 0)
 
 
if __name__ == "__main__":
    unittest.main()
 
