# gui.py
import tkinter as tk
import pickle
from fighter import Fighter, MAX_HP, Ability
from abilities import power_strike, vampiric_bite, recharge, poison_strike, burn_blast, bleeding_slash, shield_wall
import os

QTABLE_FILE = "ai_qtables.pkl"

class FightSimGUI:
    BAR_LENGTH = 200

    def __init__(self, root):
        self.root = root
        root.title("AI Fight Simulator")

        # Load Q-tables if exist
        self.qtables = self.load_qtables()

        # Text log
        self.text = tk.Text(root, width=70, height=12, font=("Consolas", 12))
        self.text.pack(padx=10, pady=5)

        # Visual frames
        self.frame_vis = tk.Frame(root)
        self.frame_vis.pack(padx=10, pady=5)

        # AI 1 visuals
        self.ai1_label = tk.Label(self.frame_vis, text="AI_One", font=("Consolas", 12, "bold"))
        self.ai1_label.grid(row=0, column=0, sticky="w")
        self.ai1_hp_canvas = tk.Canvas(self.frame_vis, width=self.BAR_LENGTH, height=20, bg="red")
        self.ai1_hp_canvas.grid(row=1, column=0, padx=5, pady=2)
        self.ai1_status_label = tk.Label(self.frame_vis, text="", font=("Consolas", 10))
        self.ai1_status_label.grid(row=2, column=0, sticky="w")
        self.ai1_wins_label = tk.Label(self.frame_vis, text="Wins: 0", font=("Consolas", 10, "bold"))
        self.ai1_wins_label.grid(row=3, column=0, sticky="w")

        # AI 2 visuals
        self.ai2_label = tk.Label(self.frame_vis, text="AI_Two", font=("Consolas", 12, "bold"))
        self.ai2_label.grid(row=0, column=1, sticky="w")
        self.ai2_hp_canvas = tk.Canvas(self.frame_vis, width=self.BAR_LENGTH, height=20, bg="red")
        self.ai2_hp_canvas.grid(row=1, column=1, padx=5, pady=2)
        self.ai2_status_label = tk.Label(self.frame_vis, text="", font=("Consolas", 10))
        self.ai2_status_label.grid(row=2, column=1, sticky="w")
        self.ai2_wins_label = tk.Label(self.frame_vis, text="Wins: 0", font=("Consolas", 10, "bold"))
        self.ai2_wins_label.grid(row=3, column=1, sticky="w")

        # Win counters
        self.ai1_wins = 0
        self.ai2_wins = 0

        # Create fighters
        self.ai1 = Fighter("AI_One")
        self.ai2 = Fighter("AI_Two")

        # Restore Q-tables if they exist
        if "AI_One" in self.qtables:
            self.ai1.q_table = self.qtables["AI_One"]
        if "AI_Two" in self.qtables:
            self.ai2.q_table = self.qtables["AI_Two"]

        # Add abilities
        self.ai1.add_ability(Ability("Power Strike", cooldown=3, func=power_strike))
        self.ai1.add_ability(Ability("Vampiric Bite", cooldown=4, func=vampiric_bite))
        self.ai1.add_ability(Ability("Recharge", cooldown=5, func=recharge))
        self.ai1.add_ability(Ability("Bleeding Slash", cooldown=4, func=bleeding_slash))

        self.ai2.add_ability(Ability("Poison Strike", cooldown=3, func=poison_strike))
        self.ai2.add_ability(Ability("Burn Blast", cooldown=4, func=burn_blast))
        self.ai2.add_ability(Ability("Shield Wall", cooldown=5, func=shield_wall))

        self.start_new_fight()
        self.update_fight()

    # --- Logging ---
    def log(self, msg):
        self.text.insert(tk.END, msg + "\n")
        self.text.see(tk.END)

    # --- Visual updates ---
    def update_hp_bar(self, canvas, hp):
        canvas.delete("all")
        hp_ratio = max(hp, 0) / MAX_HP
        length = int(hp_ratio * self.BAR_LENGTH)
        canvas.create_rectangle(0, 0, length, 20, fill="green")
        canvas.create_rectangle(length, 0, self.BAR_LENGTH, 20, fill="red")

    def update_status_label(self, label, fighter):
        active = [s for s,v in fighter.statuses.items() if v>0]
        label.config(text="Status: " + (", ".join(active) if active else "None"))

    def update_wins_label(self):
        self.ai1_wins_label.config(text=f"Wins: {self.ai1_wins}")
        self.ai2_wins_label.config(text=f"Wins: {self.ai2_wins}")

    def update_visuals(self):
        self.update_hp_bar(self.ai1_hp_canvas, self.ai1.hp)
        self.update_hp_bar(self.ai2_hp_canvas, self.ai2.hp)
        self.update_status_label(self.ai1_status_label, self.ai1)
        self.update_status_label(self.ai2_status_label, self.ai2)
        self.update_wins_label()

    # --- Fight logic ---
    def start_new_fight(self):
        self.ai1.hp = MAX_HP
        self.ai2.hp = MAX_HP
        self.ai1.statuses.clear()
        self.ai2.statuses.clear()
        for a in self.ai1.abilities: a.cur_cd = 0
        for a in self.ai2.abilities: a.cur_cd = 0
        self.log("\n===== NEW FIGHT =====\n")
        self.update_visuals()

    def update_fight(self):
        # Check win
        if self.ai1.hp <= 0 or self.ai2.hp <= 0:
            winner = self.ai1.name if self.ai1.hp > 0 else self.ai2.name
            self.log(f"\n🏆 Winner: {winner}\n")
            if self.ai1.hp <= 0:
                self.ai2_wins += 1
                self.ai1.memory.append(-100)
                self.ai2.memory.append(100)
            else:
                self.ai1_wins += 1
                self.ai1.memory.append(100)
                self.ai2.memory.append(-100)

            # Save Q-tables after each fight
            self.save_qtables()

            self.root.after(1200, self.start_new_fight)
            self.root.after(1300, self.update_fight)
            return

        # Tick statuses and cooldowns
        for log in self.ai1.tick_statuses(): self.log(log)
        for log in self.ai2.tick_statuses(): self.log(log)
        self.ai1.tick_cooldowns()
        self.ai2.tick_cooldowns()

        # Get states
        s1 = self.ai1.get_state_key(self.ai2)
        s2 = self.ai2.get_state_key(self.ai1)

        # Choose actions
        a1 = self.ai1.choose_action(self.ai2)
        a2 = self.ai2.choose_action(self.ai1)

        # Perform actions
        log1, r1 = self.ai1.perform_action(a1, self.ai2)
        log2, r2 = self.ai2.perform_action(a2, self.ai1)
        self.log(log1)
        self.log(log2)

        # Update Q-learning
        ns1 = self.ai1.get_state_key(self.ai2)
        ns2 = self.ai2.get_state_key(self.ai1)
        self.ai1.update_q(s1, a1, r1, ns1)
        self.ai2.update_q(s2, a2, r2, ns2)

        # Update visuals
        self.update_visuals()

        # Continue the loop
        self.root.after(600, self.update_fight)

    # --- Q-table persistence ---
    def save_qtables(self):
        self.qtables["AI_One"] = self.ai1.q_table
        self.qtables["AI_Two"] = self.ai2.q_table
        with open(QTABLE_FILE, "wb") as f:
            pickle.dump(self.qtables, f)

    def load_qtables(self):
        if os.path.exists(QTABLE_FILE):
            with open(QTABLE_FILE, "rb") as f:
                return pickle.load(f)
        return {}
