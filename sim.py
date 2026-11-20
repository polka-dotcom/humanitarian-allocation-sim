
import random
 
ITEMS = ["medicine", "shelter", "nutrition"]
ZONES = ["A", "B", "C"]
ROUNDS = 10
 
 
def make_requests(seed, rounds=ROUNDS):
    rng = random.Random(seed)
    requests = []
    for rnd in range(rounds):
        for _ in range(rng.randint(3, 5)):
            requests.append({
                "id": len(requests),
                "zone": rng.choice(ZONES),
                "item": rng.choice(ITEMS),
                "qty": rng.randint(1, 5),
                "urgency": rng.randint(1, 3),
                "people": rng.randint(10, 100),
                "arrival": rnd,
                "given": 0,
                "filled_round": None,
            })
    return requests
 
 
def make_stock(requests, factor):
    # factor x units requested, at least 1
    stock = {}
    for item in ITEMS:
        total = sum(r["qty"] for r in requests if r["item"] == item)
        stock[item] = max(1, round(factor * total))
    return stock
 
 
def new_game(seed, factor, rounds=ROUNDS):
    requests = make_requests(seed, rounds)
    return {"requests": requests, "stock": make_stock(requests, factor), "round": 0,
            "seed": seed, "rounds": rounds}
 
 
def pending(state):
    # arrived and not fully filled
    return [r for r in state["requests"]
            if r["arrival"] <= state["round"] and r["given"] < r["qty"]]
 
 
def give(state, req, units):
    # capped by units needed and stock left
    units = min(units, req["qty"] - req["given"], state["stock"][req["item"]])
    if units <= 0:
        return 0
    req["given"] += units
    state["stock"][req["item"]] -= units
    if req["given"] == req["qty"]:
        req["filled_round"] = state["round"]
    return units
 
 
def finished(state):
    return state["round"] >= state["rounds"]
 
 
def play(seed, factor, agent, rounds=ROUNDS):
    # agent returns ordered list of (request, units, reason)
    state = new_game(seed, factor, rounds)
    log = []
    while not finished(state):
        for req, units, reason in agent(state):
            got = give(state, req, units)
            if got:
                log.append((state["round"], req["id"], got, reason))
        state["round"] += 1
    return state, log
 
 
def jain(values):
    total = sum(values)
    squares = sum(v * v for v in values)
    if squares == 0:
        return 0.0
    return total * total / (len(values) * squares)
 
 
def metrics(state):
    reqs = state["requests"]
 
    served = sum(r["people"] * r["given"] / r["qty"] for r in reqs)
 
    # never filled counts as filled in the round after the last one
    delays = []
    for r in reqs:
        end = state["rounds"] if r["filled_round"] is None else r["filled_round"]
        delays.append(end - r["arrival"])
    delay = sum(delays) / len(delays)
 
    # served ratio per zone, skipping zones with no requests
    ratios = []
    for zone in ZONES:
        zone_reqs = [r for r in reqs if r["zone"] == zone]
        if not zone_reqs:
            continue
        asked = sum(r["people"] for r in zone_reqs)
        got = sum(r["people"] * r["given"] / r["qty"] for r in zone_reqs)
        ratios.append(got / asked)
    fairness = jain(ratios)
 
    # share of urgency 3 requests fully filled
    urgent = [r for r in reqs if r["urgency"] == 3]
    if urgent:
        urgent_filled = sum(r["given"] == r["qty"] for r in urgent) / len(urgent)
    else:
        urgent_filled = 1.0
 
    return {"served": served, "delay": delay, "fairness": fairness,
            "urgent_filled": urgent_filled}
 
