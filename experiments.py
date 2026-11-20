import csv
import statistics
import sys

import sim
from agents import AGENTS

SETTINGS = {"scarce": 0.5, "ample": 0.8}
MEASURES = ["served", "delay", "fairness", "urgent_filled"]
PAIRS = [("Fuzzy+FSM", "Greedy"), ("Fuzzy+FSM", "Fuzzy")]


def main():
    # "tune" uses seeds 0 to 9, otherwise report seeds 100 to 129
    tuning = len(sys.argv) > 1 and sys.argv[1] == "tune"
    seeds = range(0, 10) if tuning else range(100, 130)
    tag = "tune" if tuning else "report"

    rows = []
    for setting, factor in SETTINGS.items():
        for name, agent in AGENTS.items():
            for seed in seeds:
                state, _ = sim.play(seed, factor, agent)
                m = sim.metrics(state)
                rows.append({"setting": setting, "agent": name, "seed": seed, **m})

    with open(f"results_runs_{tag}.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["setting", "agent", "seed"] + MEASURES)
        writer.writeheader()
        writer.writerows(rows)

    summary = []
    for setting in SETTINGS:
        for name in AGENTS:
            runs = [r for r in rows if r["setting"] == setting and r["agent"] == name]
            line = {"setting": setting, "agent": name, "runs": len(runs)}
            for measure in MEASURES:
                values = [r[measure] for r in runs]
                line[measure + "_mean"] = statistics.mean(values)
                line[measure + "_sd"] = statistics.stdev(values)
            summary.append(line)

    with open(f"results_summary_{tag}.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(summary[0]))
        writer.writeheader()
        writer.writerows(summary)

    # same seeds for every agent, so compare agents seed by seed
    paired = []
    for setting in SETTINGS:
        for a_name, b_name in PAIRS:
            for measure in MEASURES:
                a = {r["seed"]: r[measure] for r in rows
                     if r["setting"] == setting and r["agent"] == a_name}
                b = {r["seed"]: r[measure] for r in rows
                     if r["setting"] == setting and r["agent"] == b_name}
                diffs = [a[seed] - b[seed] for seed in seeds]
                paired.append({"setting": setting, "agent": a_name, "minus": b_name,
                               "measure": measure,
                               "mean_diff": statistics.mean(diffs),
                               "std_error": statistics.stdev(diffs) / len(diffs) ** 0.5})

    with open(f"results_paired_{tag}.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(paired[0]))
        writer.writeheader()
        writer.writerows(paired)

    print(f"{tag} seeds {seeds.start} to {seeds.stop - 1}")
    print(f"{'setting':8} {'agent':8} {'served':>16} {'delay':>14} {'fairness':>14} {'urgent filled':>15}")
    for s in summary:
        print(f"{s['setting']:8} {s['agent']:8} "
              f"{s['served_mean']:9.1f} ±{s['served_sd']:5.1f} "
              f"{s['delay_mean']:7.2f} ±{s['delay_sd']:4.2f} "
              f"{s['fairness_mean']:7.3f} ±{s['fairness_sd']:5.3f} "
              f"{s['urgent_filled_mean']:7.3f} ±{s['urgent_filled_sd']:5.3f}")


    print()
    print("paired differences (first agent minus second), mean and standard error")
    for p in paired:
        print(f"{p['setting']:8} {p['agent']} - {p['minus']:7} {p['measure']:14} "
              f"{p['mean_diff']:9.3f} (se {p['std_error']:.3f})")


main()
