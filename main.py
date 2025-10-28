import sys

from ga_train import train_and_save, load_best
from battle import simulate_fight
from agents import Agent
from gui import FightSimGUI
import tkinter as tk


def demo():
    try:
        best = load_best()
    except Exception:
        print("No saved best agent found. Train first with `python main.py train`.")
        return
    rand_agent = Agent()
    winner, a_hp, b_hp, logs = simulate_fight(best, rand_agent)
    print("Demo fight between best (A) and random (B):")
    for line in logs[:50]:
        print(line)
    print("Result:", winner, "A_hp", a_hp, "B_hp", b_hp)


def main():
    if len(sys.argv) < 2:
        # default: launch GUI
        root = tk.Tk()
        FightSimGUI(root)
        root.mainloop()
        return
    cmd = sys.argv[1]
    if cmd == "train":
        train_and_save()
    elif cmd == "demo":
        demo()
    elif cmd == "gui":
        root = tk.Tk()
        FightSimGUI(root)
        root.mainloop()
    else:
        print("Unknown command:", cmd)


if __name__ == "__main__":
    main()
