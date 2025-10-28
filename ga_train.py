import random
import numpy as np
import pickle
from agents import Agent
from battle import simulate_fight

BEST_PATH = "best_agent.pkl"

class GASettings:
    population = 60
    generations = 80
    elite_frac = 0.15
    mutation_rate = 0.12
    mutation_scale = 0.18
    evaluate_rounds = 4


def evaluate_agent(agent, population, rounds=4):
    # play against a few opponents randomly chosen from population
    opponents = random.sample(population, min(len(population), rounds))
    wins = 0
    score = 0.0
    for opp in opponents:
        winner, a_hp, b_hp, _ = simulate_fight(agent, opp)
        if winner=="A":
            wins += 1
            score += 1.0 + (a_hp/100.0)
        elif winner=="B":
            score += (a_hp/100.0)
        else:
            score += 0.5
    # average
    return wins/len(opponents), score/len(opponents)


def run_generation(pop):
    # evaluate all
    results = []
    for i,agent in enumerate(pop):
        win_rate, avg_score = evaluate_agent(agent, pop, rounds=GASettings.evaluate_rounds)
        results.append((agent, win_rate, avg_score))
    # sort by avg_score
    results.sort(key=lambda x: x[2], reverse=True)
    return results


def evolve(pop):
    results = run_generation(pop)
    N = len(pop)
    elite_n = max(1, int(N * GASettings.elite_frac))
    elites = [r[0] for r in results[:elite_n]]
    new_pop = elites.copy()
    # fill rest
    while len(new_pop) < N:
        a,b = random.sample(elites, 2) if len(elites)>1 else (elites[0], elites[0])
        child = Agent.crossover(a,b, mix_rate=0.5)
        child.mutate(rate=GASettings.mutation_rate, scale=GASettings.mutation_scale)
        new_pop.append(child)
    return new_pop, results


def train_and_save(pop_size=GASettings.population, generations=GASettings.generations, status_cb=None):
    """Train GA and optionally report progress via status_cb(message).
    status_cb: callable that accepts a single string (like self.log in GUI)."""
    pop = [Agent() for _ in range(pop_size)]
    best = None
    for gen in range(1,generations+1):
        pop, results = evolve(pop)
        best_agent, best_win, best_score = results[0]
        msg = f"Gen {gen}: best_score={best_score:.3f} win_rate={best_win:.3f}"
        if status_cb:
            status_cb(msg)
        else:
            print(msg)
        best = best_agent
        # occasional save
        if gen%10==0:
            with open(BEST_PATH, "wb") as f:
                pickle.dump(best.get_params(), f)
    # final save
    with open(BEST_PATH, "wb") as f:
        pickle.dump(best.get_params(), f)
    final_msg = f"Training complete. Best saved to {BEST_PATH}"
    if status_cb:
        status_cb(final_msg)
    else:
        print(final_msg)
    return best


def load_best(path=BEST_PATH):
    with open(path, "rb") as f:
        w,b = pickle.load(f)
    return Agent.from_params(w,b)


if __name__=="__main__":
    train_and_save()
