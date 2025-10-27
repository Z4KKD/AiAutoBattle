import random

def power_strike(user, opp):
    hit_chance = 0.82
    if random.random() > hit_chance:
        return f"{user.name} uses Power Strike but misses!", -1.0
    dmg = random.randint(20, 32)
    # Bonus if charged
    if user.statuses.get("charged",0) > 0:
        dmg = int(dmg * 1.5)
        user.statuses["charged"] = 0
    opp.hp -= dmg
    opp.clamp_hp()
    return f"{user.name} uses Power Strike for {dmg} damage!", dmg * 0.12

def vampiric_bite(user, opp):
    dmg = random.randint(10, 18)
    heal = dmg // 2
    # Extra bonus if opp is poisoned or bleeding
    if opp.statuses.get("poison",0) > 0 or opp.statuses.get("bleed",0) > 0:
        dmg = int(dmg * 1.2)
        heal = int(heal * 1.2)
    opp.hp -= dmg
    user.hp += heal
    user.clamp_hp()
    opp.clamp_hp()
    return f"{user.name} bites {opp.name} for {dmg} and heals {heal} HP!", (dmg * 0.09 + heal * 0.05)

def recharge(user, opp):
    user.statuses["charged"] = 2
    user.hp += 4
    user.clamp_hp()
    return f"{user.name} uses Recharge and stores energy (2 turns).", 1.5

def poison_strike(user, opp):
    dmg = random.randint(6, 12)
    opp.hp -= dmg
    opp.statuses["poison"] = max(opp.statuses.get("poison", 0), 3)
    opp.clamp_hp()
    return f"{user.name} hits and poisons {opp.name} for {dmg} damage! (3 turns)", dmg * 0.08

def burn_blast(user, opp):
    dmg = random.randint(7, 13)
    opp.hp -= dmg
    opp.statuses["burn"] = max(opp.statuses.get("burn", 0), 3)
    opp.clamp_hp()
    # Combo bonus if opponent is already poisoned
    bonus = " Extra burn synergy!" if opp.statuses.get("poison",0)>0 else ""
    return f"{user.name} blasts {opp.name} and applies burn (3 turns).{bonus}", dmg * 0.09

def bleeding_slash(user, opp):
    dmg = random.randint(9, 14)
    opp.hp -= dmg
    opp.statuses["bleed"] = max(opp.statuses.get("bleed", 0), 2)
    opp.clamp_hp()
    # Reward if following poison strike
    bonus = " Combo synergy with Poison Strike!" if "Poison Strike" in user.combo_memory else ""
    return f"{user.name} slashes {opp.name}, causing bleeding (2 turns).{bonus}", dmg * 0.085

def shield_wall(user, opp):
    user.statuses["shield_wall"] = 2
    user.hp += 3
    user.clamp_hp()
    return f"{user.name} raises Shield Wall (damage reduction, 2 turns).", 1.2
