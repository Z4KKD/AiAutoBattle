import tkinter as tk
import pickle
from fighter import Fighter, MAX_HP, Ability
from abilities import power_strike, vampiric_bite, recharge, poison_strike, burn_blast, bleeding_slash, shield_wall
import os, random, heapq

QTABLE_FILE = "ai_qtables.pkl"
GRID_SIZE = 15
TILE_SIZE = 40
VISION_RANGE = 7

class FightSimGUI:
    BAR_LENGTH = 200

    def __init__(self, root):
        self.root = root
        root.title("AI Fight Simulator")

        # Load Q-tables
        self.qtables = self.load_qtables()

        # Logging area
        self.text = tk.Text(root, width=70, height=12, font=("Consolas",12))
        self.text.pack(padx=10,pady=5)

        # Canvas
        self.canvas = tk.Canvas(root, width=GRID_SIZE*TILE_SIZE, height=GRID_SIZE*TILE_SIZE+80, bg="black")
        self.canvas.pack(padx=10,pady=5)

        # Win counters
        self.ai1_wins = 0
        self.ai2_wins = 0

        # Fighters
        self.ai1 = Fighter("AI_One")
        self.ai2 = Fighter("AI_Two")
        if "AI_One" in self.qtables: self.ai1.q_table = self.qtables["AI_One"]
        if "AI_Two" in self.qtables: self.ai2.q_table = self.qtables["AI_Two"]

        # Add abilities
        self.ai1.add_ability(Ability("Power Strike",3,power_strike))
        self.ai1.add_ability(Ability("Vampiric Bite",4,vampiric_bite))
        self.ai1.add_ability(Ability("Recharge",5,recharge))
        self.ai1.add_ability(Ability("Bleeding Slash",4,bleeding_slash))

        self.ai2.add_ability(Ability("Poison Strike",3,poison_strike))
        self.ai2.add_ability(Ability("Burn Blast",4,burn_blast))
        self.ai2.add_ability(Ability("Shield Wall",5,shield_wall))

        self.init_maze()
        self.start_new_fight()
        self.update_fight()

    # ---------------- Maze ----------------
    def init_maze(self):
        # Start empty maze
        self.maze = [[0]*GRID_SIZE for _ in range(GRID_SIZE)]
        for i in range(GRID_SIZE):
            self.maze[0][i] = self.maze[GRID_SIZE-1][i] = 1
            self.maze[i][0] = self.maze[i][GRID_SIZE-1] = 1

        # Function to check connectivity using BFS
        def is_connected():
            visited = [[False]*GRID_SIZE for _ in range(GRID_SIZE)]
            queue = [(1,1)]
            visited[1][1] = True
            count = 1
            while queue:
                x,y = queue.pop(0)
                for dx,dy in [(0,-1),(0,1),(-1,0),(1,0)]:
                    nx,ny = x+dx,y+dy
                    if 0<=nx<GRID_SIZE and 0<=ny<GRID_SIZE and not visited[ny][nx] and self.maze[ny][nx]==0:
                        visited[ny][nx] = True
                        queue.append((nx,ny))
                        count += 1
            # Check that most tiles are reachable
            empty_tiles = sum(row.count(0) for row in self.maze)
            return count >= empty_tiles

        # Randomly add walls without blocking connectivity
        wall_count = int(GRID_SIZE*GRID_SIZE*0.25)  # 25% walls
        while wall_count > 0:
            x,y = random.randint(1,GRID_SIZE-2), random.randint(1,GRID_SIZE-2)
            if self.maze[y][x]==0:
                self.maze[y][x] = 1
                if not is_connected():
                    self.maze[y][x] = 0  # revert if it blocks maze
                else:
                    wall_count -= 1


    def draw_maze(self):
        self.canvas.delete("all")
        for y,row in enumerate(self.maze):
            for x,cell in enumerate(row):
                color = "grey" if cell else "black"
                self.canvas.create_rectangle(x*TILE_SIZE, y*TILE_SIZE, (x+1)*TILE_SIZE, (y+1)*TILE_SIZE, fill=color, outline="white")
        self.draw_fighter(self.ai1,"blue")
        self.draw_fighter(self.ai2,"red")
        self.draw_hp_bar(self.ai1, 20, GRID_SIZE*TILE_SIZE+10, "blue")
        self.draw_hp_bar(self.ai2, 300, GRID_SIZE*TILE_SIZE+10, "red")
        self.canvas.create_text(100, GRID_SIZE*TILE_SIZE+50, text=f"Wins: {self.ai1.name} {self.ai1_wins}", fill="white", font=("Arial",12,"bold"))
        self.canvas.create_text(400, GRID_SIZE*TILE_SIZE+50, text=f"Wins: {self.ai2.name} {self.ai2_wins}", fill="white", font=("Arial",12,"bold"))

    def draw_fighter(self,fighter,color):
        x,y = fighter.pos
        self.canvas.create_rectangle(x*TILE_SIZE+5, y*TILE_SIZE+5, (x+1)*TILE_SIZE-5, (y+1)*TILE_SIZE-5, fill=color)
        offset = 0
        for s in fighter.statuses:
            if fighter.statuses[s]>0:
                self.canvas.create_text(x*TILE_SIZE+20, y*TILE_SIZE+10+offset, text=s[0].upper(), fill="yellow", font=("Arial",10,"bold"))
                offset += 12

    def draw_hp_bar(self, fighter, x, y, color):
        frac = fighter.hp / fighter.max_hp
        self.canvas.create_rectangle(x, y, x+self.BAR_LENGTH, y+15, fill="grey")
        self.canvas.create_rectangle(x, y, x+self.BAR_LENGTH*frac, y+15, fill=color)
        self.canvas.create_text(x+self.BAR_LENGTH/2, y+7, text=f"{fighter.hp}/{fighter.max_hp}", fill="white", font=("Arial",10,"bold"))

    # ---------------- Logging ----------------
    def log(self,msg):
        self.text.insert(tk.END,msg+"\n")
        self.text.see(tk.END)

    # ---------------- Fight setup ----------------
    def start_new_fight(self):
        for f in [self.ai1,self.ai2]:
            f.hp = MAX_HP
            f.statuses.clear()
            for a in f.abilities: a.cur_cd = 0

        while True:
            x1,y1 = random.randint(1,GRID_SIZE-2), random.randint(1,GRID_SIZE-2)
            x2,y2 = random.randint(1,GRID_SIZE-2), random.randint(1,GRID_SIZE-2)
            if self.maze[y1][x1]==0 and self.maze[y2][x2]==0 and abs(x1-x2)+abs(y1-y2)>6:
                self.ai1.pos = (x1,y1)
                self.ai2.pos = (x2,y2)
                break

        self.log("\n===== NEW FIGHT =====\n")
        self.draw_maze()

    # ---------------- Fight update ----------------
    def update_fight(self):
        for f in [self.ai1,self.ai2]:
            for log in f.tick_statuses(): self.log(log)
            f.tick_cooldowns()

        ax,ay = self.ai1.pos
        bx,by = self.ai2.pos
        dist = abs(ax-bx)+abs(ay-by)

        visible1 = self.can_see(self.ai1,self.ai2)
        visible2 = self.can_see(self.ai2,self.ai1)

        # Sneak attack: crit first hit if only one sees the other
        sneak_attacker = None
        if visible1 != visible2:
            sneak_attacker = self.ai1 if not visible1 else self.ai2
            self.log(f"💥 {sneak_attacker.name} performs a sneak attack!")

        # Movement
        if dist>1 or not visible1: self.ai_move(self.ai1,self.ai2, visible1)
        if dist>1 or not visible2: self.ai_move(self.ai2,self.ai1, visible2)

        self.draw_maze()

        if dist <= 1 and (visible1 or visible2):
            self.zoom_fight(sneak_attacker)

        # Check win
        if self.ai1.hp<=0 or self.ai2.hp<=0:
            winner = self.ai1.name if self.ai1.hp>0 else self.ai2.name
            self.log(f"\n🏆 Winner: {winner}\n")
            if winner==self.ai1.name: self.ai1_wins +=1
            else: self.ai2_wins +=1
            self.save_qtables()
            self.root.after(1200,self.start_new_fight)
            self.root.after(1300,self.update_fight)
            return

        self.root.after(300,self.update_fight)  # faster updates

    # ---------------- Visibility ----------------
    def can_see(self, ai, opp):
        ax,ay = ai.pos
        bx,by = opp.pos
        return abs(ax-bx)+abs(ay-by) <= VISION_RANGE

    # ---------------- AI movement with pathfinding ----------------
    def ai_move(self, ai, opp, sees_opponent):
        if ai.statuses.get("stunned",0)>0: return
        steps_per_turn = 2
        for _ in range(steps_per_turn):
            path = self.find_path(ai.pos, opp.pos if sees_opponent else None)
            if path and len(path)>1:
                ai.pos = path[1]  # move next step along path
            else:
                # fallback random move
                ax,ay = ai.pos
                move_options = [(ax+dx, ay+dy) for dx,dy in [(0,-1),(0,1),(-1,0),(1,0)]
                                if 0<=ax+dx<GRID_SIZE and 0<=ay+dy<GRID_SIZE and self.maze[ay+dy][ax+dx]==0]
                if move_options:
                    ai.pos = random.choice(move_options)

    def find_path(self, start, goal):
        # Simple BFS for pathfinding if goal exists
        if goal is None: return None
        queue = [(start, [start])]
        visited = set()
        while queue:
            pos, path = queue.pop(0)
            if pos==goal: return path
            if pos in visited: continue
            visited.add(pos)
            x,y = pos
            for dx,dy in [(0,-1),(0,1),(-1,0),(1,0)]:
                nx,ny = x+dx,y+dy
                if 0<=nx<GRID_SIZE and 0<=ny<GRID_SIZE and self.maze[ny][nx]==0:
                    queue.append(((nx,ny), path+[(nx,ny)]))
        return None

    # ---------------- Zoomed fight ----------------
    def zoom_fight(self, sneak_attacker=None):
        self.canvas.delete("all")
        self.canvas.create_rectangle(50,50,250,250,fill="blue")
        self.canvas.create_rectangle(350,50,550,250,fill="red")
        self.draw_hp_bar(self.ai1, 50, 20, "blue")
        self.draw_hp_bar(self.ai2, 350, 20, "red")

        # Determine action order for sneak attack
        if sneak_attacker==self.ai1:
            order = [(self.ai1,self.ai2),(self.ai2,self.ai1)]
        elif sneak_attacker==self.ai2:
            order = [(self.ai2,self.ai1),(self.ai1,self.ai2)]
        else:
            order = [(self.ai1,self.ai2),(self.ai2,self.ai1)]

        for attacker, defender in order:
            a = attacker.choose_action(defender)
            log,r = attacker.perform_action(a, defender)
            self.log(log)
            self.animate_action(a, 50 if attacker==self.ai1 else 350, 50, defender)
            ns = attacker.get_state_key(defender)
            attacker.update_q(attacker.get_state_key(defender), a, r, ns)

    # ---------------- Action animation ----------------
    def animate_action(self, action, x, y, target):
        if "attack" in action.lower() or "strike" in action.lower() or "slash" in action.lower():
            tx,ty = target.pos
            self.animate_attack(x,y,tx*TILE_SIZE+5,ty*TILE_SIZE+5,"yellow")
        elif "heal" in action.lower() or action=="Recharge":
            self.animate_heal(x,y)
        elif "defend" in action.lower() or "shield" in action.lower():
            self.animate_shield(x,y)

    def animate_attack(self,x1,y1,x2,y2,color="yellow",duration=200):
        proj = self.canvas.create_oval(x1+40,y1+100,x1+50,y1+110,fill=color)
        steps = 10
        dx = (x2-x1)/steps
        dy = (y2-y1)/steps
        def move_proj(step=0):
            if step<steps:
                self.canvas.move(proj,dx,dy)
                self.root.after(duration//steps, lambda: move_proj(step+1))
            else:
                self.canvas.delete(proj)
        move_proj()

    def animate_heal(self,x,y):
        heal = self.canvas.create_text(x+45,y+120,text="+HP",fill="green",font=("Arial",12,"bold"))
        self.root.after(600, lambda: self.canvas.delete(heal))

    def animate_shield(self,x,y):
        shield = self.canvas.create_rectangle(x+35,y+105,x+55,y+125,outline="cyan",width=3)
        self.root.after(600, lambda: self.canvas.delete(shield))

    # ---------------- Q-table persistence ----------------
    def save_qtables(self):
        self.qtables["AI_One"] = self.ai1.q_table
        self.qtables["AI_Two"] = self.ai2.q_table
        with open(QTABLE_FILE,"wb") as f:
            pickle.dump(self.qtables,f)

    def load_qtables(self):
        if os.path.exists(QTABLE_FILE):
            with open(QTABLE_FILE,"rb") as f:
                return pickle.load(f)
        return {}
