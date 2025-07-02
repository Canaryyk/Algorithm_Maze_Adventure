import tkinter
import customtkinter
import os
import json
import math
import copy
import itertools
from heapq import heappush, heappop
from tkinter import filedialog
from PIL import Image, ImageTk, ImageGrab

# -------------------------------
# 技能释放与估值逻辑 (核心算法)
# -------------------------------

def get_available_skills(state, skills):
    return [s for s in skills if state["skill_cooldowns"].get(s["id"], 0) == 0]

def apply_skill(state, skill, skills):
    new_state = {
        "boss_hps": state["boss_hps"].copy(),
        "skill_cooldowns": state["skill_cooldowns"].copy(),
        "turns_elapsed": state["turns_elapsed"] + 1,
        "current_boss": state["current_boss"]
    }

    if new_state["current_boss"] < len(new_state["boss_hps"]):
        new_state["boss_hps"][new_state["current_boss"]] -= skill["damage"]
        while (new_state["current_boss"] < len(new_state["boss_hps"]) and 
               new_state["boss_hps"][new_state["current_boss"]] <= 0):
            new_state["current_boss"] += 1

    new_state["skill_cooldowns"][skill["id"]] = skill["cooldown"] + 1
    return new_state

def compute_avg_damage(state, skills):
    cooldowns = state["skill_cooldowns"]
    total_weighted_dmg = 0
    total_weight = 0

    for skill in skills:
        cid = skill["id"]
        cooldown = cooldowns.get(cid, 0)
        weight = 1.0 / (cooldown + 1)
        total_weighted_dmg += skill["damage"] * weight
        total_weight += weight

    return total_weighted_dmg / total_weight if total_weight > 0 else 1.0

def optimize_boss_fight(input_data):
    boss_hps = input_data["B"]
    player_skills = [
        {"id": i, "damage": s[0], "cooldown": s[1]}
        for i, s in enumerate(input_data["PlayerSkills"])
    ]
    if not boss_hps or not player_skills: return [], "输入数据不足"

    initial_state = {
        "boss_hps": boss_hps.copy(),
        "skill_cooldowns": {s["id"]: 0 for s in player_skills},
        "turns_elapsed": 0,
        "current_boss": 0
    }

    counter = itertools.count()
    pq = [(compute_avg_damage(initial_state, player_skills), 0, next(counter), initial_state, [])]
    best_solution_turns = float('inf')
    best_skill_sequence = None
    visited = {}
    
    # 增加一个迭代次数限制，防止无限循环
    max_iterations = 200000 
    iterations = 0

    while pq and iterations < max_iterations:
        iterations += 1
        f_n, turns_elapsed, _, state, skill_sequence = heappop(pq)

        key = (
            tuple(state["boss_hps"]),
            tuple(sorted(state["skill_cooldowns"].items())),
            state["current_boss"]
        )
        if key in visited and visited[key] <= turns_elapsed:
            continue
        visited[key] = turns_elapsed

        if f_n >= best_solution_turns:
            continue

        if state["current_boss"] >= len(state["boss_hps"]):
            if turns_elapsed < best_solution_turns:
                best_solution_turns = turns_elapsed
                best_skill_sequence = skill_sequence
            continue

        current_state = copy.deepcopy(state)
        for skill_id in current_state["skill_cooldowns"]:
            if current_state["skill_cooldowns"][skill_id] > 0:
                current_state["skill_cooldowns"][skill_id] -= 1

        available_skills = get_available_skills(current_state, player_skills)
        if not available_skills: # 如果没有可用技能，则必须等待
             new_state = copy.deepcopy(current_state)
             new_state["turns_elapsed"] += 1
             new_turns = turns_elapsed + 1
             new_sequence = skill_sequence + [-1] # -1 代表等待
             
             remaining_hp = sum(hp for hp in new_state["boss_hps"][new_state["current_boss"]:] if hp > 0)
             if remaining_hp > 0:
                 avg_dmg = compute_avg_damage(new_state, player_skills)
                 h_n = math.ceil(remaining_hp / avg_dmg) if avg_dmg > 0 else float('inf')
                 new_f_n = new_turns + h_n
                 if new_f_n < best_solution_turns:
                    heappush(pq, (new_f_n, new_turns, next(counter), new_state, new_sequence))
        else:
            for skill in available_skills:
                new_state = apply_skill(current_state, skill, player_skills)
                new_turns = turns_elapsed + 1
                new_sequence = skill_sequence + [skill["id"]]

                remaining_hp = sum(hp for hp in new_state["boss_hps"][new_state["current_boss"]:] if hp > 0)
                
                if remaining_hp > 0:
                    avg_dmg = compute_avg_damage(new_state, player_skills)
                    h_n = math.ceil(remaining_hp / avg_dmg) if avg_dmg > 0 else float('inf')
                    new_f_n = new_turns + h_n
                    if new_f_n < best_solution_turns:
                        heappush(pq, (new_f_n, new_turns, next(counter), new_state, new_sequence))
                else: # Boss已被击败
                    if new_turns < best_solution_turns:
                         best_solution_turns = new_turns
                         best_skill_sequence = new_sequence
                    # 提前结束循环的一个分支
                    heappush(pq, (new_turns, new_turns, next(counter), new_state, new_sequence))


    if best_skill_sequence is None:
        return [], f"在 {max_iterations} 次迭代内未找到解。"

    return best_skill_sequence, None

# -------------------------------
# GUI 应用
# -------------------------------

class BossFightOptimizerApp(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.title("boss战斗实现")
        self.geometry("800x850")
        customtkinter.set_appearance_mode("Light")
        customtkinter.set_default_color_theme("blue")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- 图片资源 ---
        self.player_pil_image = None
        self.boss_pil_image = None
        self.player_photo_image = None # For canvas
        self.boss_photo_image = None   # For canvas

        # --- 保存动画所需数据 ---
        self.animation_data = {}
        self.animation_job = None
        self.canvas_objects = {}
        
        # --- 战斗动画画布 (移动到顶部) ---
        self.canvas_frame = customtkinter.CTkFrame(self)
        self.canvas_frame.grid(row=0, column=0, padx=20, pady=(10, 5), sticky="nsew")
        self.canvas_frame.grid_rowconfigure(0, weight=1)
        self.canvas_frame.grid_columnconfigure(0, weight=1)

        self.canvas = tkinter.Canvas(self.canvas_frame, bg="white", highlightthickness=0)
        self.canvas.grid(row=0, column=0, sticky="nsew")

        # --- 输入框架 ---
        self.input_frame = customtkinter.CTkFrame(self)
        self.input_frame.grid(row=1, column=0, padx=20, pady=5, sticky="nsew")
        self.input_frame.grid_columnconfigure(1, weight=1)
        
        self.load_button = customtkinter.CTkButton(self.input_frame, text="从 JSON 文件加载数据", command=self.load_from_file)
        self.load_button.grid(row=0, column=0, columnspan=2, padx=10, pady=(10,5), sticky="ew")

        self.boss_hp_label = customtkinter.CTkLabel(self.input_frame, text="Boss 生命值 (用逗号隔开):")
        self.boss_hp_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.boss_hp_entry = customtkinter.CTkEntry(self.input_frame, placeholder_text="例如: 100, 200, 150")
        self.boss_hp_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        # --- 技能管理 与 控制输出 框架 (合并) ---
        self.main_frame = customtkinter.CTkFrame(self)
        self.main_frame.grid(row=2, column=0, padx=20, pady=(5, 10), sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=3) 
        self.main_frame.grid_columnconfigure(1, weight=1) 
        self.main_frame.grid_rowconfigure(0, weight=1)

        # --- 技能管理 (现在在右侧) ---
        self.skills_frame = customtkinter.CTkFrame(self.main_frame)
        self.skills_frame.grid(row=0, column=1, padx=(5, 10), pady=10, sticky="nsew")
        self.skills_frame.grid_columnconfigure(0, weight=1)

        self.skills_label = customtkinter.CTkLabel(self.skills_frame, text="玩家技能列表", font=customtkinter.CTkFont(size=16, weight="bold"))
        self.skills_label.grid(row=0, column=0, columnspan=3, padx=10, pady=10)
        
        self.skill_listbox = tkinter.Listbox(self.skills_frame, bg="#2b2b2b", fg="white", borderwidth=0, highlightthickness=0, selectbackground="#1f6aa5", font=("Segoe UI", 12), height=8)
        self.skill_listbox.grid(row=1, column=0, columnspan=3, padx=10, pady=10, sticky="ew")

        self.remove_skill_button = customtkinter.CTkButton(self.skills_frame, text="移除选中技能", command=self.remove_skill, fg_color="transparent", border_width=2, text_color=("gray10", "#DCE4EE"))
        self.remove_skill_button.grid(row=2, column=0, columnspan=3, padx=10, pady=10, sticky="ew")

        # --- 控制与输出 (现在在左侧，更宽) ---
        self.control_frame = customtkinter.CTkFrame(self.main_frame)
        self.control_frame.grid(row=0, column=0, padx=(10, 5), pady=10, sticky="nsew")
        self.control_frame.grid_columnconfigure(0, weight=1)
        self.control_frame.grid_rowconfigure(3, weight=1)

        self.run_button = customtkinter.CTkButton(self.control_frame, text="开始战斗", command=self.run_optimization, font=customtkinter.CTkFont(size=16, weight="bold"))
        self.run_button.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        
        self.play_button = customtkinter.CTkButton(self.control_frame, text="播放战斗动画", command=self.start_animation, state="disabled")
        self.play_button.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

        self.output_label = customtkinter.CTkLabel(self.control_frame, text="战斗结果:", anchor="w")
        self.output_label.grid(row=2, column=0, padx=10, pady=(10, 0), sticky="ew")
        self.output_textbox = customtkinter.CTkTextbox(self.control_frame, state="disabled", font=customtkinter.CTkFont(family="Consolas", size=12))
        self.output_textbox.grid(row=3, column=0, padx=10, pady=(0, 10), sticky="nsew")

        self.load_character_images()

    def load_character_images(self):
        """
        从预设路径加载角色图片。
        请将下面的示例路径替换为您的图片实际路径。
        """
        try:
            # --- 在这里替换为您图片的真实路径 ---
            player_image_path = "D:/Users/H1594/Desktop/player.png" 
            boss_image_path = "D:/Users/H1594/Desktop/boss.png"
            # ------------------------------------

            player_img = Image.open(player_image_path)
            player_img.thumbnail((80, 80), Image.Resampling.LANCZOS)
            self.player_pil_image = player_img

            boss_img = Image.open(boss_image_path)
            boss_img.thumbnail((80, 80), Image.Resampling.LANCZOS)
            self.boss_pil_image = boss_img
            
            print("玩家和Boss图片加载成功。")

        except FileNotFoundError:
            print("提示: 未在代码中预设的路径找到玩家或Boss图片, 将使用默认图形。")
            print("如需使用图片, 请在 `load_character_images` 函数中设置正确的图片路径。")
        except Exception as e:
            print(f"加载角色图片时发生错误: {e}")

    def remove_skill(self):
        selected_indices = self.skill_listbox.curselection()
        for i in reversed(selected_indices):
            self.skill_listbox.delete(i)

    def load_from_file(self, file_path=None):
        if not file_path:
            file_path = filedialog.askopenfilename(
                title="选择一个 JSON 文件",
                filetypes=(("JSON files", "*.json"), ("All files", "*.*"))
            )
        if not file_path:
            return

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            self.boss_hp_entry.delete(0, tkinter.END)
            self.boss_hp_entry.insert(0, ", ".join(map(str, data.get("B", []))))

            self.skill_listbox.delete(0, tkinter.END)
            for skill in data.get("PlayerSkills", []):
                self.skill_listbox.insert(tkinter.END, f"伤害: {skill[0]}, 冷却: {skill[1]}")
            
            self.show_info("加载成功", f"已成功从 {os.path.basename(file_path)} 加载数据。")

        except Exception as e:
            self.show_error("文件读取错误", f"无法加载或解析文件: {e}")

    def run_optimization(self):
        # --- 清理旧状态 ---
        if self.animation_job:
            self.after_cancel(self.animation_job)
            self.animation_job = None
        
        self.canvas.delete("all") # 清空画布
        
        self.play_button.configure(state="disabled")
        
        self.output_textbox.configure(state="normal")
        self.output_textbox.delete("1.0", tkinter.END)
        self.output_textbox.insert("1.0", "正在计算，请稍候...\n\n")
        self.update_idletasks() # 强制更新UI

        try:
            # 解析 Boss HP
            boss_hps = [int(hp.strip()) for hp in self.boss_hp_entry.get().split(',') if hp.strip()]
            if not boss_hps:
                raise ValueError("Boss 生命值不能为空。")

            # 解析技能
            skills = []
            for i in range(self.skill_listbox.size()):
                line = self.skill_listbox.get(i)
                parts = line.replace(",", "").split()
                # 伤害: D, 冷却: C -> ['伤害:', 'D', '冷却:', 'C']
                damage = int(parts[1])
                cooldown = int(parts[3])
                skills.append([damage, cooldown])
            if not skills:
                raise ValueError("玩家技能列表不能为空。")

            input_data = {
                "B": boss_hps,
                "PlayerSkills": skills
            }

            sequence, error_msg = optimize_boss_fight(input_data)
            
            self.output_textbox.delete("1.0", tkinter.END)
            if error_msg:
                 self.output_textbox.insert("1.0", f"计算出错: {error_msg}\n")
            elif sequence:
                skill_map = {i: f"技能{i+1} (D:{s[0]}, C:{s[1]})" for i, s in enumerate(skills)}
                skill_map[-1] = "等待" # 等待回合
                
                readable_sequence = [skill_map[sid] for sid in sequence]
                
                output_str = f"战斗完成！\n"
                output_str += f"--------------------------------\n"
                output_str += f"最小回合数: {len(sequence)}\n\n"
                output_str += f"最优技能序列 (ID):\n{sequence}\n\n"
                output_str += f"最优技能序列 (详细):\n"
                output_str += "\n".join(f"回合 {i+1}: {name}" for i, name in enumerate(readable_sequence))
                output_str += "\n\n准备就绪，点击“播放战斗动画”查看。"
                
                self.output_textbox.insert("1.0", output_str)

                # 保存动画数据并启用按钮
                self.animation_data = {
                    "sequence": sequence,
                    "initial_boss_hps": boss_hps,
                    "skills": skills,
                    "skill_map": skill_map,
                }
                self.setup_battle_scene(boss_hps) # 新函数：设置战斗场景
                self.play_button.configure(state="normal")

            else:
                self.output_textbox.insert("1.0", "未找到可行的技能序列。\n请检查输入数据是否合理。")

        except ValueError as e:
            self.show_error("输入错误", str(e))
            self.output_textbox.delete("1.0", tkinter.END)
            self.output_textbox.insert("1.0", f"输入错误: {e}")
        except Exception as e:
            self.show_error("运行时错误", f"发生未知错误: {e}")
            self.output_textbox.delete("1.0", tkinter.END)
            self.output_textbox.insert("1.0", f"运行时错误: {e}")
        
        self.run_button.configure(state="normal")
        self.output_textbox.configure(state="disabled")

    def setup_battle_scene(self, boss_hps):
        self.canvas.delete("all")
        self.canvas_objects = {"bosses": [], "player": {}}
        self.player_photo_image = None
        self.boss_photo_image = None
        
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        # 玩家
        player_x, player_y = canvas_width / 2, canvas_height * 0.8
        if self.player_pil_image:
            self.player_photo_image = ImageTk.PhotoImage(self.player_pil_image)
            self.canvas_objects["player"]["body"] = self.canvas.create_image(player_x, player_y, image=self.player_photo_image)
        else:
            self.canvas_objects["player"]["body"] = self.canvas.create_oval(player_x-20, player_y-20, player_x+20, player_y+20, fill="#3b8ed0", outline="black", width=2)
        
        self.canvas_objects["player"]["text"] = self.canvas.create_text(player_x, player_y + 50, text="玩家", fill="black", font=("Segoe UI", 12, "bold"))

        # Bosses
        num_bosses = len(boss_hps)
        spacing = canvas_width / (num_bosses + 1)
        for i, hp in enumerate(boss_hps):
            boss_x = spacing * (i + 1)
            boss_y = canvas_height * 0.3
            boss_info = {}

            if self.boss_pil_image:
                if i == 0:
                     self.boss_photo_image = ImageTk.PhotoImage(self.boss_pil_image)
                boss_info["body"] = self.canvas.create_image(boss_x, boss_y, image=self.boss_photo_image)
            else:
                boss_info["body"] = self.canvas.create_rectangle(boss_x-25, boss_y-25, boss_x+25, boss_y+25, fill="#a53b3b", outline="black", width=2)
            
            boss_info["text"] = self.canvas.create_text(boss_x, boss_y - 50, text=f"Boss {i+1}", fill="black", font=("Segoe UI", 12, "bold"))
            
            # HP Bar
            bar_y = boss_y + 50
            boss_info["hp_bar_bg"] = self.canvas.create_rectangle(boss_x-50, bar_y-8, boss_x+50, bar_y+8, fill="#e0e0e0", outline="")
            boss_info["hp_bar"] = self.canvas.create_rectangle(boss_x-50, bar_y-8, boss_x+50, bar_y+8, fill="#5cb85c", outline="")
            boss_info["hp_text"] = self.canvas.create_text(boss_x, bar_y, text=f"{hp}/{hp}", fill="black", font=("Segoe UI", 10))
            
            self.canvas_objects["bosses"].append(boss_info)

    def start_animation(self):
        if not self.animation_data:
            return

        if self.animation_job:
            self.after_cancel(self.animation_job)

        self.play_button.configure(state="disabled")
        self.run_button.configure(state="disabled")

        self.setup_battle_scene(self.animation_data["initial_boss_hps"])

        self.animation_state = {
            "current_hps": list(self.animation_data["initial_boss_hps"]),
            "current_boss_idx": 0,
            "turn": 0
        }
        self.after(500, self.run_animation_turn)

    def run_animation_turn(self):
        turn = self.animation_state["turn"]
        sequence = self.animation_data["sequence"]

        if turn >= len(sequence):
            self.play_button.configure(state="normal")
            self.run_button.configure(state="normal")
            self.animation_job = None
            return

        skill_id = sequence[turn]
        skill_map = self.animation_data["skill_map"]
        skill_name = skill_map[skill_id]
        
        # 1. 宣布技能
        status_text = self.canvas.create_text(self.canvas.winfo_width()/2, self.canvas.winfo_height()/2, text=f"回合 {turn+1}: 使用 {skill_name}", fill="blue", font=("Segoe UI", 16, "bold"))
        
        if skill_id == -1: # 等待回合
            self.animation_job = self.after(1000, lambda: [
                self.canvas.delete(status_text),
                self.animation_state.update({"turn": turn + 1}),
                self.run_animation_turn()
            ])
        else:
            self.animation_job = self.after(800, self.animate_projectile, status_text)

    def animate_projectile(self, status_text_id):
        self.canvas.delete(status_text_id)

        player_coords = self.canvas.coords(self.canvas_objects["player"]["body"])
        px, py = player_coords[0], player_coords[1]
        
        boss_idx = self.animation_state["current_boss_idx"]
        boss_coords = self.canvas.coords(self.canvas_objects["bosses"][boss_idx]["body"])
        bx, by = boss_coords[0], boss_coords[1]

        projectile = self.canvas.create_oval(px-8, py-8, px+8, py+8, fill="#3b8ed0", outline="black")

        steps = 20
        dx = (bx - px) / steps
        dy = (by - py) / steps
        
        self._move_projectile(projectile, dx, dy, steps)

    def _move_projectile(self, projectile_id, dx, dy, steps_left):
        if steps_left > 0:
            self.canvas.move(projectile_id, dx, dy)
            self.animation_job = self.after(20, self._move_projectile, projectile_id, dx, dy, steps_left - 1)
        else:
            self.canvas.delete(projectile_id)
            self.animate_hit_effect()

    def animate_hit_effect(self):
        turn = self.animation_state["turn"]
        sequence = self.animation_data["sequence"]
        skill_id = sequence[turn]
        skills = self.animation_data["skills"]
        skill_damage = skills[skill_id][0]

        boss_idx = self.animation_state["current_boss_idx"]
        boss_body_id = self.canvas_objects["bosses"][boss_idx]["body"]
        coords = self.canvas.coords(boss_body_id)
        x, y = coords[0], coords[1]
        
        # 闪烁效果
        if self.boss_photo_image: # 图片闪烁
            w, h = self.boss_photo_image.width(), self.boss_photo_image.height()
            flash = self.canvas.create_rectangle(x - w/2, y - h/2, x + w/2, y + h/2, fill="white", stipple="gray50", outline="")
            self.after(150, lambda: self.canvas.delete(flash))
        else: # 形状闪烁
            original_color = self.canvas.itemcget(boss_body_id, "fill")
            self.canvas.itemconfig(boss_body_id, fill="white")
            self.after(150, lambda: self.canvas.itemconfig(boss_body_id, fill=original_color))
        
        # 伤害数字
        damage_text = self.canvas.create_text(x, y - 30, text=f"-{skill_damage}", fill="red", font=("Impact", 20, "bold"))
        self._float_damage_text(damage_text, 20)
        
        # 更新血量
        self.animation_state["current_hps"][boss_idx] -= skill_damage
        self.update_boss_hp_display(boss_idx)

        # 检查Boss是否被击败
        self.animation_job = self.after(800, self.check_boss_defeat)
    
    def _float_damage_text(self, text_id, steps_left):
        if steps_left > 0:
            self.canvas.move(text_id, 0, -2)
            self.canvas.itemconfig(text_id, fill=f"#{int(255-((20-steps_left)*10)):02x}0000") # Fade to black
            self.after(30, self._float_damage_text, text_id, steps_left - 1)
        else:
            self.canvas.delete(text_id)

    def update_boss_hp_display(self, boss_idx):
        boss_info = self.canvas_objects["bosses"][boss_idx]
        initial_hp = self.animation_data["initial_boss_hps"][boss_idx]
        current_hp = max(0, self.animation_state["current_hps"][boss_idx])
        
        # 更新文本
        self.canvas.itemconfig(boss_info["hp_text"], text=f"{current_hp}/{initial_hp}")
        
        # 更新血条
        bar_coords = self.canvas.coords(boss_info["hp_bar_bg"])
        bar_width = bar_coords[2] - bar_coords[0]
        hp_ratio = current_hp / initial_hp
        self.canvas.coords(boss_info["hp_bar"], bar_coords[0], bar_coords[1], bar_coords[0] + bar_width * hp_ratio, bar_coords[3])

    def check_boss_defeat(self):
        boss_idx = self.animation_state["current_boss_idx"]
        current_hp = self.animation_state["current_hps"][boss_idx]

        if current_hp <= 0:
            boss_body_id = self.canvas_objects["bosses"][boss_idx]["body"]
            if self.boss_photo_image:
                 # 简易的灰度效果：在图片上覆盖一个半透明的灰色矩形
                 dim_overlay = self.canvas.create_rectangle(self.canvas.bbox(boss_body_id), fill="black", stipple="gray50", outline="")
                 self.canvas_objects["bosses"][boss_idx]["dim_overlay"] = dim_overlay
            else:
                 self.canvas.itemconfig(boss_body_id, fill="#404040", outline="gray")
            
            self.animation_state["current_boss_idx"] += 1

        self.animation_state["turn"] += 1
        self.animation_job = self.after(200, self.run_animation_turn)

    def show_error(self, title, message):
        error_dialog = customtkinter.CTkToplevel(self)
        error_dialog.title(title)
        error_dialog.geometry("300x150")
        error_dialog.transient(self)
        label = customtkinter.CTkLabel(error_dialog, text=message, wraplength=280)
        label.pack(expand=True, padx=20, pady=20)
        ok_button = customtkinter.CTkButton(error_dialog, text="确定", command=error_dialog.destroy)
        ok_button.pack(pady=10)

    def show_info(self, title, message):
        info_dialog = customtkinter.CTkToplevel(self)
        info_dialog.title(title)
        info_dialog.geometry("300x150")
        info_dialog.transient(self)
        label = customtkinter.CTkLabel(info_dialog, text=message, wraplength=280)
        label.pack(expand=True, padx=20, pady=20)
        ok_button = customtkinter.CTkButton(info_dialog, text="好的", command=info_dialog.destroy)
        ok_button.pack(pady=10)


if __name__ == "__main__":
    app = BossFightOptimizerApp()
    app.mainloop()
