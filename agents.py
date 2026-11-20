import random

import sim


def fcfs(state):
    # arrival order
    order = sorted(sim.pending(state), key=lambda r: (r["arrival"], r["id"]))
    return [(r, r["qty"] - r["given"], "first come, first served") for r in order]


def random_order(state):
    # random and repeated (seed and round)
    rng = random.Random(state["seed"] * 100 + state["round"])
    order = sim.pending(state)
    rng.shuffle(order)
    return [(r, r["qty"] - r["given"], "random order") for r in order]


def greedy(state):
    # highest urgency x people first
    order = sorted(sim.pending(state), key=lambda r: (-r["urgency"] * r["people"], r["id"]))
    return [(r, r["qty"] - r["given"],
             f"urgency {r['urgency']} x people {r['people']} = {r['urgency'] * r['people']}")
            for r in order]


AGENTS = {"FCFS": fcfs, "Random": random_order, "Greedy": greedy}
