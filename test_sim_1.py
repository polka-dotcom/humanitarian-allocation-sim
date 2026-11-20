import unittest

import sim


def fill_in_arrival_order(state):
    """A trivial agent used only for testing: ask for everything, oldest first."""
    return [(r, r["qty"], "test") for r in sim.pending(state)]


class SimTests(unittest.TestCase):
    def test_stock_never_negative_and_never_overgiven(self):
        for seed in range(20):
            for factor in (0.5, 0.8):
                state = sim.new_game(seed, factor)
                start = dict(state["stock"])
                state, _ = sim.play(seed, factor, fill_in_arrival_order)
                for item in sim.ITEMS:
                    given = sum(r["given"] for r in state["requests"] if r["item"] == item)
                    self.assertGreaterEqual(state["stock"][item], 0)
                    self.assertEqual(given + state["stock"][item], start[item])

    def test_same_seed_same_requests(self):
        self.assertEqual(sim.make_requests(5), sim.make_requests(5))
        self.assertNotEqual(sim.make_requests(5), sim.make_requests(6))

    def test_metrics_match_hand_calculation(self):
        # Three requests built by hand. Nutrition stock is only 2, so the
        # request for 4 can only be half filled (this also tests the stock limit).
        def req(i, zone, item, qty, people, arrival):
            return {"id": i, "zone": zone, "item": item, "qty": qty, "urgency": 1,
                    "people": people, "arrival": arrival, "given": 0, "filled_round": None}
        r0 = req(0, "A", "medicine", 2, 100, 0)
        r1 = req(1, "B", "nutrition", 4, 40, 1)
        r2 = req(2, "A", "shelter", 1, 10, 2)
        state = {"requests": [r0, r1, r2], "round": 0,
                 "stock": {"medicine": 5, "shelter": 5, "nutrition": 2}}
        sim.give(state, r0, 2)                  # round 0: filled
        state["round"] = 1
        self.assertEqual(sim.give(state, r1, 4), 2)   # only 2 in stock
        state["round"] = 3
        sim.give(state, r2, 1)                  # round 3: filled, arrived in round 2

        m = sim.metrics(state)
        self.assertAlmostEqual(m["served"], 100 + 20 + 10)
        # delays: r0 = 0, r1 = ROUNDS - 1 = 9 (never filled), r2 = 1
        self.assertAlmostEqual(m["delay"], (0 + 9 + 1) / 3)
        # zone A ratio 1.0, zone B ratio 0.5, zone C skipped: (1.5)^2 / (2 x 1.25)
        self.assertAlmostEqual(m["fairness"], 0.9)

    def test_jain_is_one_for_equal_values(self):
        self.assertAlmostEqual(sim.jain([0.5, 0.5, 0.5]), 1.0)
        self.assertAlmostEqual(sim.jain([0.2, 0.2]), 1.0)
        self.assertLess(sim.jain([1.0, 0.0, 0.0]), 0.5)


if __name__ == "__main__":
    unittest.main()
