import random
import numpy as np
from agents import ACTIONS

MAX_HP = 100

class Combatant:
    def __init__(self, agent, name="Agent"):
        self.agent = agent
        self.name = name
        self.hp = MAX_HP
        self.shield_turns = 0
        self.power_cd = 0

    def features_against(self, opp):
        # features: own_hp_frac, opp_hp_frac, own_shield_flag, opp_shield_flag, random_noise
        return np.array([
            self.hp / MAX_HP,
            opp.hp / MAX_HP,
            1.0 if self.shield_turns>0 else 0.0,
            1.0 if opp.shield_turns>0 else 0.0,
            random.random()
        ], dtype=float)

    def apply_action(self, action, opp):
        log = ""
        if action=="attack":
            dmg = random.randint(8,14)
            if opp.shield_turns>0:
                dmg = dmg//2
            opp.hp -= dmg
            log = f"{self.name} attacks for {dmg}."
        elif action=="defend":
            self.shield_turns = 1
            log = f"{self.name} defends (shield 1 turn)."
        elif action=="heal":
            heal = random.randint(4,8)
            self.hp = min(MAX_HP, self.hp + heal)
            log = f"{self.name} heals {heal}."
        elif action=="power":
            if self.power_cd>0:
                # fallback to attack
                dmg = random.randint(6,10)
                if opp.shield_turns>0:
                    dmg = dmg//2
                opp.hp -= dmg
                log = f"{self.name} tried Power (on cooldown) and fallback attacks for {dmg}."
            else:
                dmg = random.randint(18,28)
                if opp.shield_turns>0:
                    dmg = dmg//2
                opp.hp -= dmg
                self.power_cd = 3
                log = f"{self.name} uses Power for {dmg}."
        else:
            # unknown => minor attack
            dmg = random.randint(5,9)
            if opp.shield_turns>0:
                dmg = dmg//2
            opp.hp -= dmg
            log = f"{self.name} fallback hits for {dmg}."

        # update statuses
        if self.shield_turns>0:
            self.shield_turns = max(0, self.shield_turns-1)
        if self.power_cd>0:
            self.power_cd -= 1
        # clamp
        self.hp = max(0, min(self.hp, MAX_HP))
        opp.hp = max(0, min(opp.hp, MAX_HP))
        return log


def simulate_fight(agent_a, agent_b, max_turns=200):
    a = Combatant(agent_a, name="A")
    b = Combatant(agent_b, name="B")

    logs = []
    turn = 0
    while a.hp>0 and b.hp>0 and turn < max_turns:
        turn += 1
        # A acts
        fa = a.features_against(b)
        act_a = agent_a.act(fa)
        logs.append(a.apply_action(act_a, b))
        if b.hp<=0:
            break
        # B acts
        fb = b.features_against(a)
        act_b = agent_b.act(fb)
        logs.append(b.apply_action(act_b, a))
        # next
    winner = None
    if a.hp>0 and b.hp<=0:
        winner = "A"
    elif b.hp>0 and a.hp<=0:
        winner = "B"
    else:
        # tie -> higher HP
        if a.hp > b.hp:
            winner = "A"
        elif b.hp > a.hp:
            winner = "B"
        else:
            winner = "draw"
    return winner, a.hp, b.hp, logs
