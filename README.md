# AiAutoBattle — GA-based rewrite

This is a simplified rewrite of the original auto-battle project. Instead of per-fight Q-learning in a GUI, this version ships a compact population-based Genetic Algorithm (GA) that evolves simple linear-policy agents.

Files added:

- `agents.py` — Agent representation: linear weights -> action scores, with crossover/mutation and serialization.
- `battle.py` — Deterministic turn-based simulator used to evaluate agents.
- `ga_train.py` — Small GA trainer: population, elitism, crossover, mutation, and periodic saving of the best agent to `best_agent.pkl`.
- `main.py` — Lightweight CLI (overwrites previous GUI-based main) to run `train` or `demo`.

Why this design?
- GA avoids complex per-fight Q-table state explosion and gives a clear population-level learning signal.
- Linear policies are fast to evaluate, easy to serialize, and interpretable.
- This is an approachable base for later upgrades (neural nets, Elo-style matchmaking, or a web GUI).

Quick start

1. Install dependencies:

```powershell
pip install -r requirements.txt
```

2. Train (this runs a headless GA):

```powershell
python main.py train
```

3. Run a short demo using the saved best agent (after training):

```powershell
python main.py demo
```

Notes and next steps

- You can tweak GA parameters in `ga_train.GASettings`.
- Next improvements: add evaluation vs fixed scripted opponents, add logging of population diversity, or replace linear policies with small neural networks (still lightweight with numpy).
