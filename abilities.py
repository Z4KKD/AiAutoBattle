import random

def power_strike(user, opp):
    hit_chance = 0.82
    if random.random() > hit_chance:
        return f"{user.name} uses Power Strike but misses!", -1.0
    dmg = random.randint(20, 32)
    opp.hp -= dmg
    opp.clamp_hp()
    return f"{user.name} uses Power Strike for {dmg} damage!", dmg * 0.12

def vampiric_bite(user, opp):
    dmg = random.randint(10, 18)
    heal = dmg // 2
    opp.hp -= dmg
    user.hp += heal
    user.clamp_hp()
    opp.clamp_hp()
    return f"{user.name} bites {opp.name} for {dmg} and heals {heal} HP!", (dmg * 0.09 + heal * 0.05)

def recharge(user, opp):
    user.statuses["charged"] = 2
    user.hp += 4
    user.clamp_hp()
    return f"{user.name} uses Recharge and stores energy.", 1.5

def poison_strike(user, opp):
    dmg = random.randint(6, 12)
    opp.hp -= dmg
    opp.statuses["poison"] = max(opp.statuses.get("poison", 0), 3)
    opp.clamp_hp()
    return f"{user.name} hits and poisons {opp.name} for {dmg} damage! (3 turns)", dmg * 0.08 + 0.03

def burn_blast(user, opp):
    dmg = random.randint(7, 13)
    opp.hp -= dmg
    opp.statuses["burn"] = max(opp.statuses.get("burn", 0), 3)
    opp.clamp_hp()
    return f"{user.name} blasts {opp.name} and applies burn (3 turns).", dmg * 0.09 + 0.03

def bleeding_slash(user, opp):
    dmg = random.randint(9, 14)
    opp.hp -= dmg
    opp.statuses["bleed"] = max(opp.statuses.get("bleed", 0), 2)
    opp.clamp_hp()
    return f"{user.name} slashes {opp.name}, causing bleeding (2 turns).", dmg * 0.085 + 0.02

def shield_wall(user, opp):
    user.statuses["shield_wall"] = 2
    user.hp += 3
    user.clamp_hp()
    return f"{user.name} raises Shield Wall (damage reduction).", 1.2

def stun_blow(user, opp):
    chance = 0.5
    dmg = random.randint(6, 10)
    opp.hp -= dmg
    if random.random() < chance:
        opp.statuses["stunned"] = 1
        effect = " and stuns the opponent!"
    else:
        effect = ""
    opp.clamp_hp()
    return f"{user.name} hits {opp.name} for {dmg} damage{effect}", dmg * 0.09 + (0.05 if "stunned" in opp.statuses else 0)

def multi_hit_combo(user, opp):
    hits = random.randint(2, 3)
    total_dmg = 0
    for _ in range(hits):
        dmg = random.randint(4, 8)
        opp.hp -= dmg
        total_dmg += dmg
    opp.clamp_hp()
    return f"{user.name} hits {opp.name} {hits} times for {total_dmg} total damage!", total_dmg * 0.08

def drain_life(user, opp):
    dmg = random.randint(8, 14)
    heal = dmg // 2
    opp.hp -= dmg
    user.hp += heal
    user.clamp_hp()
    opp.clamp_hp()
    return f"{user.name} drains {dmg} HP from {opp.name} and heals {heal} HP!", dmg*0.08 + heal*0.05
