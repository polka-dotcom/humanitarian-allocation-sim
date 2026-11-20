# humanitarian-allocation-sim
CSCI218 group project, Case C: Emergency Resource Allocation Simulation.

You're acting as an aid coordinator. 
Requests for medicine, shelter and nutrition arrive each round, and stock is limited. You decide who gets what. Afterwards an AI plays the same scenario, explains each decision and is scored on the same measures.

## Requirements

Python 3 with Tkinter.

## Run

- Play the game: `python game.py`
- Run the experiments: `python experiments.py`
- Run the tests: `python test_sim.py` and `python test_agents.py`

## How the game works

- 3 supplies (medicine, shelter, nutrition) and 3 zones (A, B, C). Up to 10 rounds (adjustable), with 3 to 5 new requests per round.
- Each request has a zone, supply, quantity, urgency (Low, Medium, High), number of people affected and an arrival round.
- Stock is a share of everything requested: 0.5 for scarce, 0.8 for ample. There is no restocking.
- In the game, pick a request, set the units and press Give. Press End round when finished. Press Suggest (AI) to see what the AI would do next and why.

## AI assistance

Claude (Anthropic) was used to design and plan the tests and draft this documentation
