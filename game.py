import random
import tkinter as tk
from tkinter import ttk

import sim
from agents import fuzzy_fsm

SETTINGS = {"scarce": 0.5, "ample": 0.8}
URGENCY = {1: "Low", 2: "Medium", 3: "High"}
COLOURS = {1: "white", 2: "#fff2cc", 3: "#ffd6d6"}
FONT = ("Consolas", 11)

# (column name, heading, width in pixels, alignment)
COLUMNS = [
    ("id", "ID", 55, "w"),
    ("zone", "Zone", 60, "w"),
    ("supply", "Supply", 110, "w"),
    ("needs", "Needs (units)", 110, "center"),
    ("urgency", "Urgency", 90, "center"),
    ("people", "People", 80, "center"),
    ("waited", "Waited (rounds)", 130, "center"),
]


def request_values(r, rnd):
    return ("#" + str(r["id"]), r["zone"], r["item"].capitalize(), r["qty"] - r["given"],
            URGENCY[r["urgency"]], r["people"], rnd - r["arrival"])


def suggestion(state):
    # first AI choice that stock allows
    for req, units, reason in fuzzy_fsm(state):
        units = min(units, state["stock"][req["item"]])
        if units > 0:
            return req, units, reason
    return None


def results_text(seed, factor, rounds, human_state):
    # AI plays the same seed, setting and number of rounds
    ai_state, ai_log = sim.play(seed, factor, fuzzy_fsm, rounds)
    you = sim.metrics(human_state)
    ai = sim.metrics(ai_state)
    diff = ai["served"] - you["served"]
    if diff > 0:
        verdict = f"The AI helped {diff:.0f} more people than you."
    elif diff < 0:
        verdict = f"You helped {-diff:.0f} more people than the AI."
    else:
        verdict = "You and the AI helped the same number of people."
    lines = [
        "GAME OVER",
        f"{'':28}{'You':>8}{'AI':>8}",
        f"{'People served':28}{you['served']:>8.0f}{ai['served']:>8.0f}",
        f"{'Average delay (rounds)':28}{you['delay']:>8.2f}{ai['delay']:>8.2f}",
        f"{'Fairness (1 = zones equal)':28}{you['fairness']:>8.2f}{ai['fairness']:>8.2f}",
        f"{'Urgent requests filled':28}{you['urgent_filled']:>8.0%}{ai['urgent_filled']:>8.0%}",
        "",
        verdict,
        "Lower delay is better. Higher is better for everything else.",
        "",
        "What the AI did, round by round:",
    ]
    for rnd, rid, units, reason in ai_log:
        item = ai_state["requests"][rid]["item"]
        lines.append(f"Round {rnd + 1}: {units} {item} to #{rid}   [{reason}]")
    return "\n".join(lines)


class Game:
    def __init__(self, root):
        top = tk.Frame(root)
        top.pack(fill="x", padx=8, pady=6)
        tk.Label(top, text="Stock:", font=FONT).pack(side="left")
        self.setting = tk.StringVar(value="scarce")
        for name in SETTINGS:
            tk.Radiobutton(top, text=name, value=name, variable=self.setting,
                           font=FONT).pack(side="left")
        tk.Label(top, text="Seed:", font=FONT).pack(side="left", padx=(10, 2))
        self.seed_box = tk.Entry(top, width=6, font=FONT)
        self.seed_box.pack(side="left")
        tk.Label(top, text="Rounds:", font=FONT).pack(side="left", padx=(10, 2))
        self.rounds_box = tk.Spinbox(top, from_=1, to=10, width=3, font=FONT)
        self.rounds_box.pack(side="left")
        tk.Button(top, text="New game", font=FONT, command=self.new_game).pack(side="left", padx=8)
        tk.Button(top, text="Replay seed", font=FONT, command=self.replay).pack(side="left")

        tk.Label(root, anchor="w", font=("Segoe UI", 10),
                 text="1. Click a request   2. Check the units   3. Press Give   "
                      "4. Press End round when finished").pack(fill="x", padx=8)
        tk.Label(root, anchor="w", font=("Segoe UI", 10),
                 text="Row colour shows urgency: red = high, yellow = medium, white = low. "
                      "Waited = rounds since the request arrived.").pack(fill="x", padx=8)

        self.info = tk.Label(root, font=("Consolas", 11, "bold"), anchor="w")
        self.info.pack(fill="x", padx=8, pady=(8, 4))

        style = ttk.Style()
        style.configure("Treeview", font=FONT, rowheight=26)
        style.configure("Treeview.Heading", font=("Consolas", 11, "bold"))
        self.table = ttk.Treeview(root, columns=[c[0] for c in COLUMNS], show="headings",
                                  height=10, selectmode="browse")
        for name, title, width, align in COLUMNS:
            self.table.heading(name, text=title)
            self.table.column(name, width=width, anchor=align)
        for urgency, colour in COLOURS.items():
            self.table.tag_configure(f"u{urgency}", background=colour)
        self.table.pack(fill="x", padx=8, pady=(0, 4))
        self.table.bind("<<TreeviewSelect>>", self.pick)

        bar = tk.Frame(root)
        bar.pack(fill="x", padx=8)
        tk.Label(bar, text="Units to give:", font=FONT).pack(side="left")
        self.units = tk.Spinbox(bar, from_=1, to=5, width=4, font=FONT)
        self.units.pack(side="left", padx=4)
        self.buttons = [
            tk.Button(bar, text="Give", font=FONT, command=self.give),
            tk.Button(bar, text="Suggest (AI)", font=FONT, command=self.suggest),
            tk.Button(bar, text="End round", font=FONT, command=self.end_round),
        ]
        for b in self.buttons:
            b.pack(side="left", padx=4)

        self.log = tk.Text(root, height=14, width=75, font=("Consolas", 10), wrap="word",
                           state="disabled")
        self.log.pack(fill="x", padx=8, pady=6)
        self.new_game()

    def say(self, text, clear=False):
        self.log.config(state="normal")
        if clear:
            self.log.delete("1.0", "end")
        self.log.insert("end", text + "\n")
        self.log.see("end")
        self.log.config(state="disabled")

    def replay(self):
        # same seed as in the box, so the same requests again
        self.new_game(same_seed=True)

    def new_game(self, same_seed=False):
        self.seed = random.randint(1000, 9999)
        if same_seed:
            try:
                self.seed = int(self.seed_box.get())
            except ValueError:
                pass
        self.seed_box.delete(0, "end")
        self.seed_box.insert(0, str(self.seed))
        try:
            self.rounds = min(max(int(self.rounds_box.get()), 1), sim.ROUNDS)
        except ValueError:
            self.rounds = 5
        self.rounds_box.delete(0, "end")
        self.rounds_box.insert(0, str(self.rounds))
        self.factor = SETTINGS[self.setting.get()]
        self.state = sim.new_game(self.seed, self.factor, self.rounds)
        for b in self.buttons:
            b.config(state="normal")
        plural = "round" if self.rounds == 1 else "rounds"
        self.say(f"New game: {self.setting.get()} stock, seed {self.seed}, "
                 f"{self.rounds} {plural}. Round 1 started.", clear=True)
        self.refresh()

    def refresh(self):
        state = self.state
        self.shown = sorted(sim.pending(state), key=lambda r: (r["arrival"], r["id"]))
        self.table.delete(*self.table.get_children())
        if sim.finished(state):
            unfilled = len(self.shown)
            self.info.config(text=f"Game over. {unfilled} requests were never fully filled.")
            self.shown = []
            return
        stock = "   ".join(f"{i.capitalize()} {n}" for i, n in state["stock"].items())
        self.info.config(text=f"Round {state['round'] + 1} of {self.rounds}     Stock left:  {stock}")
        for i, r in enumerate(self.shown):
            self.table.insert("", "end", iid=str(i), values=request_values(r, state["round"]),
                              tags=(f"u{r['urgency']}",))

    def selected(self):
        # the request picked in the table, or None
        picked = self.table.selection()
        return int(picked[0]) if picked else None

    def pick(self, event=None):
        # units box starts at what the selected request still needs
        index = self.selected()
        if index is not None:
            r = self.shown[index]
            self.units.delete(0, "end")
            self.units.insert(0, str(r["qty"] - r["given"]))

    def give(self):
        index = self.selected()
        if index is None:
            self.say("Select a request first.")
            return
        req = self.shown[index]
        try:
            units = int(self.units.get())
        except ValueError:
            self.say("Enter a whole number of units.")
            return
        got = sim.give(self.state, req, units)
        if got:
            self.say(f"You gave {got} {req['item']} to #{req['id']}.")
        else:
            self.say("Nothing given: no stock of that item, or 0 units.")
        self.refresh()
        # keep the same row selected so the next request is ready
        if self.shown:
            row_number = min(index, len(self.shown) - 1)
            self.table.selection_set(str(row_number))
            self.pick()

    def suggest(self):
        choice = suggestion(self.state)
        if choice is None:
            self.say("AI suggests giving nothing this round.")
            return
        req, units, reason = choice
        self.say(f"AI suggests: {units} {req['item']} to #{req['id']}.   [{reason}]")
        # select that row and fill in the suggested units
        for i, r in enumerate(self.shown):
            if r is req:
                self.table.selection_set(str(i))
                self.table.see(str(i))
                self.units.delete(0, "end")
                self.units.insert(0, str(units))

    def end_round(self):
        self.state["round"] += 1
        if sim.finished(self.state):
            for b in self.buttons:
                b.config(state="disabled")
            self.say(results_text(self.seed, self.factor, self.rounds, self.state), clear=True)
        else:
            new = sum(1 for r in self.state["requests"] if r["arrival"] == self.state["round"])
            self.say(f"Round {self.state['round'] + 1} of {self.rounds} started. "
                     f"{new} new requests arrived.")
        self.refresh()


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Aid Allocation Game")
    Game(root)
    root.mainloop()
