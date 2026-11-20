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


def trap(x, a, b, c, d):
    # trapezoid membership, 1 between b and c
    if x < a or x > d:
        return 0.0
    if x < b:
        return (x - a) / (b - a)
    if x <= c:
        return 1.0
    return (d - x) / (d - c)


def tri(x, a, b, c):
    return trap(x, a, b, b, c)


def grade(x):
    # same Low, Medium, High shapes for every input and for the output (Lab 4 style)
    return {"low": trap(x, 0, 0, 0.2, 0.4),
            "medium": tri(x, 0.2, 0.5, 0.8),
            "high": trap(x, 0.6, 0.8, 1, 1)}


# output sets sampled at 101 points, used for the centroid
OUT = {name: [grade(i / 100)[name] for i in range(101)] for name in ("low", "medium", "high")}


def priority(urgency, people, wait):
    # inputs scaled to 0 to 1
    u = grade((urgency - 1) / 2)
    p = grade(people / 100)
    w = grade(min(wait / 5, 1))

    # (strength, output set); AND is min
    rules = [
        (u["high"], "high"),
        (u["medium"], "medium"),
        (u["low"], "low"),
        (min(u["medium"], p["high"]), "high"),
        (p["low"], "low"),
        (w["high"], "high"),
    ]

    # clip each output set at its rule strength, join with max, centroid
    top = bottom = 0.0
    for i in range(101):
        degree = max(min(strength, OUT[name][i]) for strength, name in rules)
        top += (i / 100) * degree
        bottom += degree
    return top / bottom if bottom else 0.0


def word(x):
    # name of the set with the highest membership
    levels = grade(x)
    return max(levels, key=levels.get)


def fuzzy(state):
    # highest fuzzy priority first
    scored = []
    for r in sim.pending(state):
        wait = state["round"] - r["arrival"]
        scored.append((priority(r["urgency"], r["people"], wait), r, wait))
    scored.sort(key=lambda s: (-s[0], s[1]["id"]))
    return [(r, r["qty"] - r["given"],
             f"priority {p:.2f}: urgency {word((r['urgency'] - 1) / 2)}, "
             f"people {word(r['people'] / 100)}, wait {word(min(wait / 5, 1))}")
            for p, r, wait in scored]


AGENTS = {"FCFS": fcfs, "Random": random_order, "Greedy": greedy, "Fuzzy": fuzzy}
