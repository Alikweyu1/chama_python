"""
Chama Microservices — Live Message Movement Diagram
Multiple messages fly through the system simultaneously.
Pure Tkinter — no external libraries needed.
"""
import tkinter as tk
from tkinter import ttk
import math
import threading
import time
import random
from datetime import datetime

# ─── Window ────────────────────────────────────────────────────
win = tk.Tk()
win.title(" Chama — Live Message Flow")
win.geometry("1150x750")
win.configure(bg="#04080f")
win.resizable(True, True)

BG      = "#04080f"
SURFACE = "#0a1020"
BORDER  = "#1a2744"
LB      = "#f59e0b"
MEMBER  = "#3b82f6"
CONTRIB = "#10b981"
LOAN    = "#ef4444"
NOTIF   = "#a855f7"
SAVINGS = "#06b6d4"
REPORT  = "#f97316"
WHITE   = "#e2e8f0"
MUTED   = "#475569"
GREEN   = "#10b981"

SERVICE_INFO = {
    "member":       (MEMBER,  ":5001", ""),
    "contribution": (CONTRIB, ":5002", ""),
    "loan":         (LOAN,    ":5003", ""),
    "notification": (NOTIF,   ":5004", ""),
    "savings":      (SAVINGS, ":5005", ""),
    "report":       (REPORT,  ":5006", ""),
}

MSG_TYPES = [
    ("Register Member",       "member",       "POST /members"),
    ("Pay Contribution",      "contribution", "POST /contributions"),
    ("Apply for Loan",        "loan",         "POST /loans"),
    ("Send SMS Alert",        "notification", "POST /notifications/send"),
    ("Check Savings",         "savings",      "GET /savings"),
    ("Financial Report",      "report",       "GET /reports/financial-summary"),
    ("Repay Loan",            "loan",         "POST /loans/repay"),
    ("Broadcast to Members",  "notification", "POST /notifications/broadcast"),
    ("View Investments",      "savings",      "GET /investments"),
    ("Member Statement",      "report",       "GET /reports/member-statement"),
    ("List Members",          "member",       "GET /members"),
    ("Contribution Summary",  "contribution", "GET /contributions/summary"),
]

# ─── Main canvas ───────────────────────────────────────────────
canvas = tk.Canvas(win, bg=BG, highlightthickness=0)
canvas.pack(fill="both", expand=True)

W, H = 1150, 750

# ─── Draw grid ─────────────────────────────────────────────────
def draw_grid():
    for x in range(0, W, 40):
        canvas.create_line(x, 0, x, H, fill="#0a1220", width=1, tags="grid")
    for y in range(0, H, 40):
        canvas.create_line(0, y, W, y, fill="#0a1220", width=1, tags="grid")

draw_grid()

# ─── Layout constants ──────────────────────────────────────────
CLIENT_X,  CLIENT_Y  = 560, 38
LB_X,      LB_Y      = 410, 135
LB_W,      LB_H      = 310, 58

# Service node positions (cx, cy) — 6 services across bottom
SVC_Y    = 360
SVC_W    = 130
SVC_H    = 58
SVC_GAP  = 160
SVC_START_X = 90

SVC_NODES = {}  # name → (cx, cy, x, y)

# ─── Node drawing helpers ───────────────────────────────────────
def draw_rounded_box(x, y, w, h, color, label, sublabel, tag="node"):
    canvas.create_rectangle(x+3, y+3, x+w+3, y+h+3, fill="#000", outline="", tags=tag)
    canvas.create_rectangle(x, y, x+w, y+h, fill=SURFACE, outline=color, width=2, tags=tag)
    canvas.create_rectangle(x, y, x+w, y+4, fill=color, outline="", tags=tag)
    cx = x + w//2
    canvas.create_text(cx, y+22, text=label,    fill=color, font=("Courier", 10, "bold"), tags=tag)
    canvas.create_text(cx, y+38, text=sublabel, fill=MUTED, font=("Courier", 8),          tags=tag)
    return cx, y + h//2

def draw_static_scene():
    # ── Title ──
    canvas.create_text(W//2, 14, text="  CHAMA MICROSERVICES — LIVE MESSAGE FLOW",
                       fill=LB, font=("Courier", 12, "bold"), tags="static")

    # ── CLIENT ──
    canvas.create_rectangle(CLIENT_X-75, CLIENT_Y, CLIENT_X+75, CLIENT_Y+44,
                            fill=SURFACE, outline=WHITE, width=2, tags="static")
    canvas.create_rectangle(CLIENT_X-75, CLIENT_Y, CLIENT_X+75, CLIENT_Y+4,
                            fill=WHITE, outline="", tags="static")
    canvas.create_text(CLIENT_X, CLIENT_Y+16, text="  CLIENT",
                       fill=WHITE, font=("Courier", 10, "bold"), tags="static")
    canvas.create_text(CLIENT_X, CLIENT_Y+34, text="HTTP Requests",
                       fill=MUTED, font=("Courier", 8), tags="static")

    # ── LOAD BALANCER ──
    canvas.create_rectangle(LB_X-3, LB_Y-3, LB_X+LB_W+3, LB_Y+LB_H+3,
                            fill="", outline=LB, width=1, dash=(3,3), tags="static")
    draw_rounded_box(LB_X, LB_Y, LB_W, LB_H, LB, "⚖️  LOAD BALANCER", ":5000  Round-Robin", "static")

    # Glow behind LB
    canvas.create_rectangle(LB_X-8, LB_Y-8, LB_X+LB_W+8, LB_Y+LB_H+8,
                            fill="", outline=LB, width=1, stipple="gray25", tags="static")

    # ── SERVICES ──
    for i, (svc_name, (color, port, icon)) in enumerate(SERVICE_INFO.items()):
        sx = SVC_START_X + i * SVC_GAP
        sy = SVC_Y
        draw_rounded_box(sx, sy, SVC_W, SVC_H, color,
                         f"{icon} {svc_name.capitalize()}", port, "static")
        # Route label above
        route = f"/{svc_name if svc_name != 'savings' else 'savings'}"
        canvas.create_text(sx + SVC_W//2, sy - 14, text=f"/{svc_name}",
                           fill=color, font=("Courier", 7), tags="static")
        SVC_NODES[svc_name] = (sx + SVC_W//2, sy + SVC_H//2, sx, sy)

    # ── Static backbone lines (Client→LB, LB→services) ──
    # Client down to LB
    canvas.create_line(CLIENT_X, CLIENT_Y+44, CLIENT_X, LB_Y+LB_H//2,
                       CLIENT_X, LB_Y+LB_H//2, LB_X+LB_W//2+80, LB_Y+LB_H//2,
                       fill=BORDER, width=1, tags="static")

    lbcx = LB_X + LB_W//2
    lbby = LB_Y + LB_H

    for i, svc_name in enumerate(SERVICE_INFO.keys()):
        cx, cy, sx, sy = SVC_NODES[svc_name]
        color = SERVICE_INFO[svc_name][0]
        canvas.create_line(lbcx, lbby, cx, sy, fill=BORDER, width=1, tags="static")

    # ── Inter-service event arrows (static dashed) ──
    inter_events = [
        ("contribution", "notification", "payment→SMS"),
        ("loan",         "notification", "alert→SMS"),
        ("member",       "notification", "welcome→SMS"),
        ("savings",      "report",       "data feed"),
    ]
    for src, dst, lbl in inter_events:
        x1, y1, _, _ = SVC_NODES[src]
        x2, y2, _, _ = SVC_NODES[dst]
        color = SERVICE_INFO[dst][0]
        mid_y = max(y1, y2) + 60
        canvas.create_line(x1, y1+29, (x1+x2)//2, mid_y,
                           x2, y2+29, smooth=True,
                           fill=color, width=1, dash=(3,3),
                           arrow=tk.LAST, arrowshape=(6,8,3), tags="static")
        canvas.create_text((x1+x2)//2, mid_y+10, text=lbl,
                           fill=color, font=("Courier", 7), tags="static")

    # ── LOG PANEL ──
    canvas.create_rectangle(20, 480, W-20, H-20,
                            fill="#000000", outline=BORDER, width=1, tags="static")
    canvas.create_rectangle(20, 480, W-20, 502,
                            fill="#0a1020", outline="", tags="static")
    canvas.create_oval(30, 487, 42, 499, fill="#ef4444", outline="")
    canvas.create_oval(48, 487, 60, 499, fill=LB,        outline="")
    canvas.create_oval(66, 487, 78, 499, fill=GREEN,     outline="")
    canvas.create_text(230, 491, text="chama-lb.log  —  live request stream",
                       fill=MUTED, font=("Courier", 8), tags="static")

    # ── CONTROLS ──
    canvas.create_text(W//2, H-8,
                       text="[AUTO SEND]  Messages automatically flow every 0.8s  |  Use controls to change speed / pause",
                       fill=MUTED, font=("Courier", 7), tags="static")

draw_static_scene()

# ─── Message packet class ───────────────────────────────────────
class Message:
    def __init__(self, msg_id, name, svc, method):
        self.id      = msg_id
        self.name    = name
        self.svc     = svc
        self.method  = method
        self.color   = SERVICE_INFO[svc][0]
        self.phase   = "to_lb"    # to_lb → to_svc → return → done
        self.px      = float(CLIENT_X)
        self.py      = float(CLIENT_Y + 44)
        self.dot     = None
        self.label   = None
        self.trail   = []
        self.done    = False
        self.alpha   = 1.0

        # Compute path waypoints
        self.lb_entry_x = LB_X + LB_W//2
        self.lb_entry_y = float(LB_Y)
        cx, cy, sx, sy  = SVC_NODES[svc]
        self.svc_x      = float(cx)
        self.svc_y      = float(sy)
        self.speed      = random.uniform(3.5, 6.5)

        # Create dot on canvas
        r = 7
        self.dot   = canvas.create_oval(
            self.px-r, self.py-r, self.px+r, self.py+r,
            fill=self.color, outline=WHITE, width=1, tags="msg")
        self.label = canvas.create_text(
            self.px, self.py - 14, text=self.name[:18],
            fill=self.color, font=("Courier", 7, "bold"), tags="msg")
        canvas.tag_raise(self.dot)
        canvas.tag_raise(self.label)

    def move_toward(self, tx, ty):
        dx = tx - self.px
        dy = ty - self.py
        dist = math.hypot(dx, dy)
        if dist < self.speed:
            self.px, self.py = tx, ty
            return True
        self.px += (dx / dist) * self.speed
        self.py += (dy / dist) * self.speed
        return False

    def step(self):
        if self.done:
            return
        if self.phase == "to_lb":
            arrived = self.move_toward(self.lb_entry_x, self.lb_entry_y)
            if arrived:
                self.phase = "at_lb"
                self.lb_wait = 0

        elif self.phase == "at_lb":
            self.lb_wait = getattr(self, "lb_wait", 0) + 1
            # flash dot bigger briefly
            if self.lb_wait == 3:
                canvas.itemconfig(self.dot, outline=LB, width=2)
            if self.lb_wait > 8:
                canvas.itemconfig(self.dot, outline=WHITE, width=1)
                self.phase = "to_svc"

        elif self.phase == "to_svc":
            arrived = self.move_toward(self.svc_x, self.svc_y)
            if arrived:
                self.phase = "at_svc"
                self.svc_wait = 0
                canvas.itemconfig(self.dot, outline=self.color, width=3)

        elif self.phase == "at_svc":
            self.svc_wait = getattr(self, "svc_wait", 0) + 1
            if self.svc_wait > 10:
                canvas.itemconfig(self.dot, outline=WHITE, width=1)
                self.phase = "return"

        elif self.phase == "return":
            arrived = self.move_toward(CLIENT_X, CLIENT_Y + 44)
            if arrived:
                self.phase = "done"
                self.done  = True
                self.cleanup()
                return

        # Draw trail
        if random.random() < 0.4:
            tr = canvas.create_oval(
                self.px-3, self.py-3, self.px+3, self.py+3,
                fill=self.color, outline="", tags="trail")
            self.trail.append((tr, 6))

        # Fade trails
        new_trail = []
        for (tid, life) in self.trail:
            life -= 1
            if life <= 0:
                canvas.delete(tid)
            else:
                # make it shrink
                try:
                    coords = canvas.coords(tid)
                    if coords:
                        cx = (coords[0]+coords[2])/2
                        cy = (coords[1]+coords[3])/2
                        r  = life * 0.4
                        canvas.coords(tid, cx-r, cy-r, cx+r, cy+r)
                    new_trail.append((tid, life))
                except:
                    pass
        self.trail = new_trail

        # Update position
        r = 7
        canvas.coords(self.dot,   self.px-r, self.py-r, self.px+r, self.py+r)
        canvas.coords(self.label, self.px,   self.py-14)
        canvas.tag_raise(self.dot)
        canvas.tag_raise(self.label)

    def cleanup(self):
        canvas.delete(self.dot)
        canvas.delete(self.label)
        for (tid, _) in self.trail:
            canvas.delete(tid)
        self.trail = []

# ─── Log panel ──────────────────────────────────────────────────
log_y    = [506]
log_items= []
MAX_LOGS = 24

def add_log(text, color=WHITE):
    now = datetime.now().strftime("%H:%M:%S")
    if log_y[0] > H - 36:
        # scroll: delete oldest
        if log_items:
            canvas.delete(log_items.pop(0))
            for lid in log_items:
                canvas.move(lid, 0, -14)
            log_y[0] -= 14
    tid = canvas.create_text(28, log_y[0], text=f"[{now}]  {text}",
                             fill=color, font=("Courier", 8), anchor="w", tags="logline")
    log_items.append(tid)
    log_y[0] += 14

# Startup logs
for msg in [
    ("[INFO] Chama Load Balancer online :5000", GREEN),
    ("[INFO] 6 microservices registered and healthy ✓", GREEN),
    ("[INFO] Health check loop active (every 10s)", "#60a5fa"),
    ("─" * 95, MUTED),
]:
    add_log(msg[0], msg[1])

# ─── Message manager ────────────────────────────────────────────
messages    = []
msg_counter = [0]
paused      = [False]
speed_mult  = [1.0]
auto_interval = [0.8]  # seconds between auto messages

def spawn_message():
    mt   = random.choice(MSG_TYPES)
    name, svc, method = mt
    msg_counter[0] += 1
    m = Message(msg_counter[0], name, svc, method)
    messages.append(m)
    color = SERVICE_INFO[svc][0]
    add_log(f"[{method}]  {name}  →  {svc.upper()} :{SERVICE_INFO[svc][1]}", color)

def auto_spawn():
    while True:
        time.sleep(auto_interval[0])
        if not paused[0]:
            if len(messages) < 18:
                win.after(0, spawn_message)

# Start auto-spawn
threading.Thread(target=auto_spawn, daemon=True).start()

# ─── Animation loop ─────────────────────────────────────────────
def animate():
    if not paused[0]:
        for m in messages[:]:
            m.step()
            if m.done:
                messages.remove(m)
    win.after(16, animate)  # ~60fps

# ─── Stats overlay ─────────────────────────────────────────────
stats_ids = {}

def draw_stats():
    for k, v in stats_ids.items():
        canvas.delete(v)
    stats_ids.clear()

    # Right side stats panel
    px, py = W - 210, 130
    canvas.create_rectangle(px, py, W-18, py+320,
                            fill=SURFACE, outline=BORDER, width=1, tags="stats_bg")
    stats_ids["bg"] = "stats_bg"

    canvas.create_text(px+96, py+14, text="LIVE STATS",
                       fill=LB, font=("Courier", 9, "bold"), tags="stats")
    stats_ids["title"] = "stats"

    canvas.create_text(px+10, py+34, text=f"Active messages: {len(messages)}",
                       fill=WHITE, font=("Courier", 8), anchor="w", tags="stats")

    canvas.create_text(px+10, py+50, text=f"Total sent:      {msg_counter[0]}",
                       fill=GREEN, font=("Courier", 8), anchor="w", tags="stats")

    canvas.create_text(px+10, py+66, text=f"Speed mult:      {speed_mult[0]:.1f}x",
                       fill=SAVINGS, font=("Courier", 8), anchor="w", tags="stats")

    canvas.create_text(px+10, py+82, text=f"Status:          {'PAUSED ⏸' if paused[0] else 'RUNNING ▶'}",
                       fill=LOAN if paused[0] else GREEN, font=("Courier", 8), anchor="w", tags="stats")

    # Per-service count
    canvas.create_text(px+10, py+102, text="── Messages per service ──",
                       fill=MUTED, font=("Courier", 7), anchor="w", tags="stats")

    svc_counts = {s: 0 for s in SERVICE_INFO}
    for m in messages:
        svc_counts[m.svc] += 1

    sy2 = py + 118
    for svc, (color, port, icon) in SERVICE_INFO.items():
        count = svc_counts[svc]
        bar_w = count * 18
        canvas.create_text(px+10, sy2, text=f"{icon} {svc[:8]:8} {count}",
                           fill=color, font=("Courier", 8), anchor="w", tags="stats")
        if bar_w > 0:
            canvas.create_rectangle(px+120, sy2-5, px+120+bar_w, sy2+5,
                                    fill=color, outline="", tags="stats")
        sy2 += 18

    # Legend colors
    canvas.create_text(px+10, sy2+10, text="── Path key ──",
                       fill=MUTED, font=("Courier", 7), anchor="w", tags="stats")
    sy2 += 26
    for svc, (color, port, icon) in SERVICE_INFO.items():
        canvas.create_oval(px+10, sy2-4, px+18, sy2+4, fill=color, outline="", tags="stats")
        canvas.create_text(px+24, sy2, text=f"{svc} {port}",
                           fill=color, font=("Courier", 7), anchor="w", tags="stats")
        sy2 += 14

    canvas.delete("stats_bg")
    canvas.create_rectangle(px, py, W-18, py+320,
                            fill=SURFACE, outline=BORDER, width=1, tags="stats_bg")
    canvas.tag_lower("stats_bg")

def stats_loop():
    draw_stats()
    win.after(300, stats_loop)

win.after(500, stats_loop)

# ─── Control buttons ────────────────────────────────────────────
ctrl_frame = tk.Frame(win, bg=SURFACE)
ctrl_frame.place(x=20, y=440, width=560, height=36)

def make_btn(parent, text, cmd, color=LB):
    return tk.Button(parent, text=text, command=cmd,
                     bg=color, fg="#000", font=("Courier", 8, "bold"),
                     relief="flat", padx=10, cursor="hand2")

def toggle_pause():
    paused[0] = not paused[0]
    btn_pause.config(text="▶  RESUME" if paused[0] else "⏸  PAUSE",
                     bg=GREEN if paused[0] else LB)

def speed_up():
    speed_mult[0] = min(speed_mult[0] + 0.5, 4.0)
    auto_interval[0] = max(0.2, auto_interval[0] - 0.15)
    for m in messages:
        m.speed = min(m.speed + 1.5, 12)

def slow_down():
    speed_mult[0] = max(0.5, speed_mult[0] - 0.5)
    auto_interval[0] = min(3.0, auto_interval[0] + 0.15)
    for m in messages:
        m.speed = max(1.5, m.speed - 1.5)

def send_burst():
    for _ in range(6):
        spawn_message()

def clear_all():
    for m in messages[:]:
        m.cleanup()
        messages.clear()
    add_log("[CTRL] All messages cleared", LOAN)

btn_pause = make_btn(ctrl_frame, "⏸  PAUSE",   toggle_pause, LB)
btn_up    = make_btn(ctrl_frame, "⚡ SPEED UP", speed_up,     SAVINGS)
btn_down  = make_btn(ctrl_frame, "🐢 SLOW DOWN",slow_down,    CONTRIB)
btn_burst = make_btn(ctrl_frame, "💥 BURST ×6", send_burst,   NOTIF)
btn_clear = make_btn(ctrl_frame, "🗑  CLEAR",   clear_all,    LOAN)

for btn in [btn_pause, btn_up, btn_down, btn_burst, btn_clear]:
    btn.pack(side="left", padx=4, pady=5)

animate()
win.mainloop()