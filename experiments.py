import csv
import statistics
import sys

import sim
from agents import AGENTS

SETTINGS = {"scarce": 0.5, "ample": 0.8}
MEASURES = ["served", "delay", "fairness", "urgent_filled"]


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

    print(f"{tag} seeds {seeds.start} to {seeds.stop - 1}")
    print(f"{'setting':8} {'agent':8} {'served':>16} {'delay':>14} {'fairness':>14} {'urgent filled':>15}")
    for s in summary:
        print(f"{s['setting']:8} {s['agent']:8} "
              f"{s['served_mean']:9.1f} ±{s['served_sd']:5.1f} "
              f"{s['delay_mean']:7.2f} ±{s['delay_sd']:4.2f} "
              f"{s['fairness_mean']:7.3f} ±{s['fairness_sd']:5.3f} "
              f"{s['urgent_filled_mean']:7.3f} ±{s['urgent_filled_sd']:5.3f}")


main()
