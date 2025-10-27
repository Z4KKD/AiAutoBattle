# fighter.py
import random
from collections import defaultdict, deque

MAX_HP = 100
HP_BUCKET = 10

def clamp(v, lo, hi):
    return max(lo, min(hi, v))

def hp_bucket(hp):
    return clamp((hp // HP_BUCKET) * HP_BUCKET, 0, MAX_HP)

class Ability:
    def __init__(self, name, cooldown=0, func=None, description=""):
        self.name = name
        self.cooldown = cooldown
        self.func = func
        self.cur_cd = 0
        self.description = description

    def ready(self):
        return self.cur_cd == 0

    def use(self):
        self.cur_cd = self.cooldown

    def tick(self):
        if self.cur_cd > 0:
            self.cur_cd -= 1

class Fighter:
    def __init__(self, name, personality_bias=None):
        self.name = name
        self.hp = MAX_HP
        self.max_hp = MAX_HP

        self.statuses = defaultdict(int)
        self.abilities = []
        self.base_actions = ["attack", "defend", "heal"]

        # Q-learning
        self.q_table = {}
        self.learning_rate = 0.12
        self.discount = 0.95
        self.epsilon = 0.18
        self.memory = deque(maxlen=50)
        self.combo_memory = deque(maxlen=3)  # track last moves for combos

        self.personality_bias = personality_bias or {"aggressive":0.0, "defensive":0.0, "balanced":0.0}
        self.last_action = None

    def clamp_hp(self):
        self.hp = clamp(self.hp, 0, self.max_hp)

    def add_ability(self, ability):
        self.abilities.append(ability)

    def tick_cooldowns(self):
        for a in self.abilities:
            a.tick()

    def tick_statuses(self):
        logs = []
        for status, dmg in [("burn",3),("poison",2),("bleed",4)]:
            if self.statuses.get(status, 0) > 0:
                self.hp -= dmg
                self.statuses[status] -= 1
                logs.append(f"{self.name} suffers {status} for {dmg} damage.")
                self.clamp_hp()
        return logs

    def derive_mood(self):
        score = sum(1 if r>0 else -1 if r<0 else 0 for r in self.memory)
        if self.hp < self.max_hp*0.3: return "scared"
        if score >= 2: return "aggressive"
        if score <= -2: return "defensive"
        return "balanced"

    def get_state_key(self, opponent):
        hp_state = (hp_bucket(self.hp), hp_bucket(opponent.hp))
        my_cds = tuple(min(2, a.cur_cd) for a in self.abilities)
        opp_cds = tuple(min(2, a.cur_cd) for a in opponent.abilities)
        statuses = tuple(1 if self.statuses.get(s,0)>0 else 0 for s in ("burn","poison","bleed","shield","shield_wall","charged","stunned"))
        opp_statuses = tuple(1 if opponent.statuses.get(s,0)>0 else 0 for s in ("burn","poison","bleed","shield","shield_wall","charged","stunned"))
        combo_state = tuple(self.combo_memory)
        return (*hp_state, my_cds, opp_cds, statuses, opp_statuses, self.derive_mood(), opponent.derive_mood(), combo_state)

    def available_actions(self):
        acts = list(self.base_actions)
        acts.extend(a.name for a in self.abilities if a.ready())
        return acts

    def choose_action(self, opponent):
        state = self.get_state_key(opponent)
        actions = self.available_actions()

        # Exploration
        if random.random() < self.epsilon or state not in self.q_table:
            choice = random.choice(actions)
            self.last_action = choice
            return choice

        # Exploitation with personality and mood bias
        qvals = self.q_table.get(state, {})
        best = None
        best_score = -1e9
        mood = state[-2]  # self mood
        for a in actions:
            base_v = qvals.get(a, 0.0)
            bias = 0.0

            # Mood-based adjustment
            if mood == "aggressive" and "attack" in a:
                bias += 0.08
            if mood == "defensive" and ("heal" in a or "defend" in a):
                bias += 0.06

            # Personality bias
            if self.personality_bias.get("aggressive",0) and "attack" in a:
                bias += self.personality_bias["aggressive"]

            # Exploit opponent vulnerabilities
            if "stunned" in opponent.statuses and opponent.statuses["stunned"] > 0 and ("attack" in a or a in [ab.name for ab in self.abilities]):
                bias += 0.05

            score = base_v + bias + random.random()*1e-6
            if score > best_score:
                best_score = score
                best = a

        self.last_action = best
        return best

    def update_q(self, state, action, reward, next_state):
        if state not in self.q_table:
            self.q_table[state] = {a:0.0 for a in self.available_actions()}
        if next_state not in self.q_table:
            self.q_table[next_state] = {a:0.0 for a in self.available_actions()}
        if action not in self.q_table[state]:
            self.q_table[state][action] = 0.0

        current = self.q_table[state][action]
        future = max(self.q_table[next_state].values(), default=0.0)
        self.q_table[state][action] = current + self.learning_rate * (reward + self.discount * future - current)
        self.memory.append(reward)

        # update combo memory
        self.combo_memory.append(action)

        # minor personality evolution
        if random.random() < 0.02:
            mood = self.derive_mood()
            if mood == "aggressive":
                self.personality_bias["aggressive"] += 0.001
            if mood == "defensive":
                self.personality_bias["defensive"] += 0.001

        # decay epsilon slightly
        self.epsilon = max(0.05, self.epsilon * 0.995)

    def perform_action(self, action_name, opponent):
        reward = 0.0
        log = ""

        # Basic actions
        if action_name == "attack":
            dmg = random.randint(8,14)
            if self.statuses.get("charged",0) > 0:
                dmg = int(dmg*1.5)
                self.statuses["charged"] = 0
                log += "Charged bonus! "
            opponent.hp -= dmg
            opponent.clamp_hp()
            log += f"{self.name} attacks for {dmg} damage."
            reward += dmg*0.1

        elif action_name == "defend":
            self.hp += 6
            self.statuses["shield"] = 1
            self.clamp_hp()
            log += f"{self.name} defends and gains 6 HP."
            reward += 0.05

        elif action_name == "heal":
            heal = random.randint(6,15)
            self.hp += heal
            self.clamp_hp()
            log += f"{self.name} heals {heal} HP."
            reward += heal*0.06

        else:
            for a in self.abilities:
                if a.name == action_name and a.ready():
                    log, r = a.func(self, opponent)
                    a.use()
                    reward += r
                    break
            else:
                dmg = random.randint(6,10)
                opponent.hp -= dmg
                opponent.clamp_hp()
                log += f"{self.name} fallback attack for {dmg} damage."
                reward += dmg*0.08

        self.clamp_hp()
        opponent.clamp_hp()

        # Combo bonus example
        combo = list(self.combo_memory)[-2:] + [action_name]
        if combo == ["Poison Strike", "Bleeding Slash"]:
            reward += 0.05
            log += " Combo bonus applied!"

        # Reward for applying status effects
        for status in ["burn","poison","bleed","stunned"]:
            if opponent.statuses.get(status,0) > 0:
                reward += 0.02

        return log, reward
