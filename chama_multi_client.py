"""
Chama Microservices — Device Clients + Auth + Live Message Flow
Clients shown as drawn devices: Phone, Laptop, Tablet, Desktop
Pure Tkinter — no external libraries needed.
"""
import tkinter as tk
import math, threading, time, random
from datetime import datetime

win = tk.Tk()
win.title("🏦 Chama — Device Clients Authenticated Message Flow")
win.geometry("1200x800")
win.configure(bg="#04080f")
win.resizable(True, True)

BG      = "#04080f"
SURFACE = "#080f1c"
BORDER  = "#1a2744"
LB      = "#f59e0b"
AUTH    = "#facc15"
MEMBER  = "#3b82f6"
CONTRIB = "#10b981"
LOAN    = "#ef4444"
NOTIF   = "#a855f7"
SAVINGS = "#06b6d4"
REPORT  = "#f97316"
WHITE   = "#e2e8f0"
MUTED   = "#475569"
GREEN   = "#10b981"
RED     = "#ef4444"

W, H = 1200, 800
canvas = tk.Canvas(win, bg=BG, highlightthickness=0, width=W, height=H)
canvas.pack(fill="both", expand=True)

# grid
for x in range(0, W, 40):
    canvas.create_line(x, 0, x, H, fill="#090d1a", width=1)
for y in range(0, H, 40):
    canvas.create_line(0, y, W, y, fill="#090d1a", width=1)

# ─── Device drawing functions ──────────────────────────────────

def draw_phone(cx, y, color, label, sublabel):
    """Draw a smartphone"""
    pw, ph = 44, 76
    x = cx - pw//2
    # body
    canvas.create_rectangle(x, y, x+pw, y+ph,
                            fill=SURFACE, outline=color, width=2, tags="static")
    # screen
    canvas.create_rectangle(x+4, y+8, x+pw-4, y+ph-14,
                            fill="#0a1a2e", outline=color, width=1, tags="static")
    # screen glow lines
    for i, lc in enumerate(["#1a3a5e","#0d2a4a","#162a40"]):
        canvas.create_line(x+6, y+14+i*8, x+pw-6, y+14+i*8,
                           fill=lc, width=1, tags="static")
    # home button
    canvas.create_oval(cx-5, y+ph-11, cx+5, y+ph-3,
                       fill=SURFACE, outline=color, width=1, tags="static")
    # camera
    canvas.create_oval(cx-3, y+3, cx+3, y+7,
                       fill=SURFACE, outline=color, width=1, tags="static")
    # speaker
    canvas.create_line(cx-6, y+5, cx+6, y+5,
                       fill=color, width=2, tags="static")
    # label
    canvas.create_text(cx, y+ph+10, text=label,
                       fill=color, font=("Courier", 8, "bold"), tags="static")
    canvas.create_text(cx, y+ph+22, text=sublabel,
                       fill=MUTED, font=("Courier", 7), tags="static")
    return cx, y + ph//2

def draw_laptop(cx, y, color, label, sublabel):
    """Draw a laptop"""
    lw, lh = 80, 52
    x = cx - lw//2
    # screen part
    canvas.create_rectangle(x+4, y, x+lw-4, y+lh-8,
                            fill=SURFACE, outline=color, width=2, tags="static")
    # screen display
    canvas.create_rectangle(x+8, y+4, x+lw-8, y+lh-12,
                            fill="#0a1a2e", outline=color, width=1, tags="static")
    # screen glow
    for i, lc in enumerate(["#1a3a5e","#0d2a4a","#162a40"]):
        canvas.create_line(x+10, y+8+i*8, x+lw-10, y+8+i*8,
                           fill=lc, width=1, tags="static")
    # webcam dot
    canvas.create_oval(cx-3, y+2, cx+3, y+6,
                       fill=color, outline="", tags="static")
    # base/keyboard
    canvas.create_rectangle(x-4, y+lh-8, x+lw+4, y+lh,
                            fill=SURFACE, outline=color, width=2, tags="static")
    # touchpad
    canvas.create_rectangle(cx-10, y+lh-7, cx+10, y+lh-2,
                            fill=SURFACE, outline=color, width=1, tags="static")
    # keyboard lines
    for ki in range(3):
        canvas.create_line(x+2, y+lh-6+ki*2, x+lw-2, y+lh-6+ki*2,
                           fill=BORDER, width=1, tags="static")
    # label
    canvas.create_text(cx, y+lh+10, text=label,
                       fill=color, font=("Courier", 8, "bold"), tags="static")
    canvas.create_text(cx, y+lh+22, text=sublabel,
                       fill=MUTED, font=("Courier", 7), tags="static")
    return cx, y + lh//2

def draw_tablet(cx, y, color, label, sublabel):
    """Draw a tablet"""
    tw, th = 58, 76
    x = cx - tw//2
    # body
    canvas.create_rectangle(x, y, x+tw, y+th,
                            fill=SURFACE, outline=color, width=2, tags="static")
    # screen
    canvas.create_rectangle(x+5, y+5, x+tw-5, y+th-16,
                            fill="#0a1a2e", outline=color, width=1, tags="static")
    # screen content
    for i, lc in enumerate(["#1a3a5e","#0d2a4a","#162a40","#1a3a5e"]):
        canvas.create_line(x+8, y+10+i*10, x+tw-8, y+10+i*10,
                           fill=lc, width=1, tags="static")
    # home button
    canvas.create_oval(cx-5, y+th-12, cx+5, y+th-4,
                       fill=SURFACE, outline=color, width=1, tags="static")
    # camera
    canvas.create_oval(cx-3, y+2, cx+3, y+6,
                       fill=SURFACE, outline=color, width=1, tags="static")
    # label
    canvas.create_text(cx, y+th+10, text=label,
                       fill=color, font=("Courier", 8, "bold"), tags="static")
    canvas.create_text(cx, y+th+22, text=sublabel,
                       fill=MUTED, font=("Courier", 7), tags="static")
    return cx, y + th//2

def draw_desktop(cx, y, color, label, sublabel):
    """Draw a desktop monitor"""
    mw, mh = 80, 58
    x = cx - mw//2
    # monitor body
    canvas.create_rectangle(x, y, x+mw, y+mh,
                            fill=SURFACE, outline=color, width=2, tags="static")
    # bezel top
    canvas.create_rectangle(x+2, y+2, x+mw-2, y+4,
                            fill=BORDER, outline="", tags="static")
    # screen
    canvas.create_rectangle(x+5, y+6, x+mw-5, y+mh-8,
                            fill="#0a1a2e", outline=color, width=1, tags="static")
    # screen content lines
    for i, lc in enumerate(["#1a3a5e","#0d2a4a","#162a40","#1a3a5e"]):
        canvas.create_line(x+8, y+10+i*8, x+mw-8, y+10+i*8,
                           fill=lc, width=1, tags="static")
    # power button
    canvas.create_oval(cx-4, y+mh-6, cx+4, y+mh-1,
                       fill=SURFACE, outline=color, width=1, tags="static")
    # stand neck
    canvas.create_rectangle(cx-4, y+mh, cx+4, y+mh+10,
                            fill=color, outline="", tags="static")
    # stand base
    canvas.create_rectangle(cx-16, y+mh+10, cx+16, y+mh+14,
                            fill=color, outline="", tags="static")
    # label
    canvas.create_text(cx, y+mh+24, text=label,
                       fill=color, font=("Courier", 8, "bold"), tags="static")
    canvas.create_text(cx, y+mh+36, text=sublabel,
                       fill=MUTED, font=("Courier", 7), tags="static")
    return cx, y + mh//2

# ─── Client definitions ────────────────────────────────────────
CLIENTS = [
    {"id": "C1", "name": "Alice",    "sub": "Mobile App",  "x": 130,  "color": "#38bdf8",
     "draw": draw_phone,   "anchor_y_offset": 38},
    {"id": "C2", "name": "Brian",    "sub": "Web Browser", "x": 360,  "color": "#fb7185",
     "draw": draw_laptop,  "anchor_y_offset": 26},
    {"id": "C3", "name": "Carol",    "sub": "Tablet",      "x": 590,  "color": "#a3e635",
     "draw": draw_tablet,  "anchor_y_offset": 38},
    {"id": "C4", "name": "David",    "sub": "Desktop PC",  "x": 820,  "color": "#e879f9",
     "draw": draw_desktop, "anchor_y_offset": 29},
]
CLIENT_Y    = 22
CLIENT_BOT  = {}  # client id → bottom anchor y

# ─── System nodes ──────────────────────────────────────────────
AUTH_X, AUTH_Y = 470, 185
AUTH_W, AUTH_H = 230, 50

LB_X, LB_Y = 340, 285
LB_W, LB_H = 490, 50

SVC_Y     = 400
SVC_W     = 118
SVC_H     = 50
SVC_GAP   = 158
SVC_START = 58

SERVICE_INFO = {
    "member":       (MEMBER,  "5001", "Member"),
    "contribution": (CONTRIB, "5002", "Contribution"),
    "loan":         (LOAN,    "5003", "Loan"),
    "notification": (NOTIF,   "5004", "Notification"),
    "savings":      (SAVINGS, "5005", "Savings"),
    "report":       (REPORT,  "5006", "Report"),
}
SVC_NODES = {}

MSG_TYPES = [
    ("Pay Contribution",     "contribution", "POST /contributions"),
    ("Apply Loan",           "loan",         "POST /loans"),
    ("Check Savings",        "savings",      "GET /savings"),
    ("Send Alert",           "notification", "POST /notifications/send"),
    ("Financial Report",     "report",       "GET /reports/financial-summary"),
    ("Register Member",      "member",       "POST /members"),
    ("View Investments",     "savings",      "GET /investments"),
    ("Repay Loan",           "loan",         "POST /loans/repay"),
    ("Broadcast SMS",        "notification", "POST /notifications/broadcast"),
    ("List Members",         "member",       "GET /members"),
    ("Contribution Summary", "contribution", "GET /contributions/summary"),
    ("Member Statement",     "report",       "GET /reports/member-statement"),
]

# ─── Box helper ────────────────────────────────────────────────
def box(x, y, w, h, color, line1, line2="", tag="static"):
    canvas.create_rectangle(x+3, y+3, x+w+3, y+h+3, fill="#000", outline="", tags=tag)
    canvas.create_rectangle(x, y, x+w, y+h, fill=SURFACE, outline=color, width=2, tags=tag)
    canvas.create_rectangle(x, y, x+w, y+4, fill=color, outline="", tags=tag)
    cx2 = x + w//2
    canvas.create_text(cx2, y+(16 if line2 else 25), text=line1,
                       fill=color, font=("Courier", 9, "bold"), tags=tag)
    if line2:
        canvas.create_text(cx2, y+35, text=line2, fill=MUTED,
                           font=("Courier", 7), tags=tag)
    return cx2, y + h//2

# ─── Draw static scene ─────────────────────────────────────────
def draw_scene():
    # Title
    canvas.create_text(W//2, 12, fill=LB, tags="static",
                       text="CHAMA MICROSERVICES  —  MULTI-DEVICE AUTHENTICATED FLOW",
                       font=("Courier", 11, "bold"))

    # ── Draw devices ──
    for cl in CLIENTS:
        bx, by = cl["draw"](cl["x"], CLIENT_Y, cl["color"], cl["name"], cl["sub"])
        # bottom anchor = where the wire leaves the device
        # different devices have different heights
        if cl["draw"] == draw_phone:
            CLIENT_BOT[cl["id"]] = (cl["x"], CLIENT_Y + 76)
        elif cl["draw"] == draw_laptop:
            CLIENT_BOT[cl["id"]] = (cl["x"], CLIENT_Y + 52)
        elif cl["draw"] == draw_tablet:
            CLIENT_BOT[cl["id"]] = (cl["x"], CLIENT_Y + 76)
        elif cl["draw"] == draw_desktop:
            CLIENT_BOT[cl["id"]] = (cl["x"], CLIENT_Y + 72)

    # device label row
    canvas.create_text(W//2, CLIENT_Y + 100, tags="static",
                       text="◀── 4 Independent Device Clients ──▶",
                       fill=MUTED, font=("Courier", 7))

    # ── Auth Service ──
    auth_cx = AUTH_X + AUTH_W//2
    box(AUTH_X, AUTH_Y, AUTH_W, AUTH_H, AUTH,
        "AUTH SERVICE", ":5000  JWT Validator")
    canvas.create_text(AUTH_X + AUTH_W - 14, AUTH_Y + 14,
                       text="🔐", font=("Courier", 10), tags="static")

    # ── Load Balancer ──
    lb_cx = LB_X + LB_W//2
    box(LB_X, LB_Y, LB_W, LB_H, LB,
        "LOAD BALANCER", ":5001  Round-Robin")

    # ── Services ──
    for i, (svc, (color, port, label)) in enumerate(SERVICE_INFO.items()):
        sx = SVC_START + i * SVC_GAP
        box(sx, SVC_Y, SVC_W, SVC_H, color, label, f":{port}")
        canvas.create_text(sx + SVC_W//2, SVC_Y - 12,
                           text=f"/{svc}", fill=color,
                           font=("Courier", 6), tags="static")
        SVC_NODES[svc] = (sx + SVC_W//2, SVC_Y + SVC_H//2)

    # ── Backbone wires ──
    for cl in CLIENTS:
        bx, by = CLIENT_BOT[cl["id"]]
        canvas.create_line(bx, by, auth_cx, AUTH_Y,
                           fill=BORDER, width=1, dash=(4,3), tags="static")

    canvas.create_line(auth_cx, AUTH_Y+AUTH_H, lb_cx, LB_Y,
                       fill=BORDER, width=1, dash=(4,3), tags="static")

    lb_bot = LB_Y + LB_H
    for svc, (cx2, cy2) in SVC_NODES.items():
        canvas.create_line(lb_cx, lb_bot, cx2, SVC_Y,
                           fill=BORDER, width=1, tags="static")

    # inter-service curves
    for src, dst, lbl in [
        ("contribution", "notification", "payment→SMS"),
        ("loan",         "notification", "alert→SMS"),
        ("savings",      "report",       "data feed"),
    ]:
        x1, y1 = SVC_NODES[src]
        x2, y2 = SVC_NODES[dst]
        my = max(y1, y2) + 55
        canvas.create_line(x1, y1+25, (x1+x2)//2, my, x2, y2+25,
                           smooth=True, fill=SERVICE_INFO[dst][0],
                           width=1, dash=(3,3),
                           arrow=tk.LAST, arrowshape=(6,8,3), tags="static")
        canvas.create_text((x1+x2)//2, my+10, text=lbl,
                           fill=SERVICE_INFO[dst][0],
                           font=("Courier", 6), tags="static")

    # ── Auth legend (right panel) ──
    canvas.create_rectangle(W-290, 185, W-20, 340,
                            fill=SURFACE, outline=BORDER, width=1, tags="static")
    canvas.create_text(W-155, 200, text="AUTH FLOW",
                       fill=AUTH, font=("Courier", 8, "bold"), tags="static")
    ay = 218
    for col, txt in [
        (WHITE,  "Device sends HTTP + JWT token"),
        (AUTH,   "Auth Service validates JWT"),
        (GREEN,  "Token OK  →  forward to LB"),
        (RED,    "Token FAIL  →  401 Rejected"),
        (LB,     "LB routes to correct service"),
        (GREEN,  "Service processes request"),
        (WHITE,  "Response returns to device"),
    ]:
        canvas.create_oval(W-287, ay-4, W-279, ay+4,
                           fill=col, outline="", tags="static")
        canvas.create_text(W-272, ay, text=txt, fill=col,
                           font=("Courier", 7), anchor="w", tags="static")
        ay += 16

    # device legend
    canvas.create_rectangle(W-290, 346, W-20, 430,
                            fill=SURFACE, outline=BORDER, width=1, tags="static")
    canvas.create_text(W-155, 360, text="DEVICES",
                       fill=WHITE, font=("Courier", 8, "bold"), tags="static")
    dy = 378
    for cl in CLIENTS:
        canvas.create_oval(W-287, dy-4, W-279, dy+4,
                           fill=cl["color"], outline="", tags="static")
        canvas.create_text(W-272, dy,
                           text=f"{cl['name']:6}  {cl['sub']}",
                           fill=cl["color"], font=("Courier", 7), anchor="w", tags="static")
        dy += 14

    # ── Log panel ──
    canvas.create_rectangle(20, 520, W-20, H-46,
                            fill="#000", outline=BORDER, width=1, tags="static")
    canvas.create_rectangle(20, 520, W-20, 540,
                            fill=SURFACE, outline="", tags="static")
    canvas.create_oval(30,526,42,538, fill=RED,   outline="")
    canvas.create_oval(48,526,60,538, fill=LB,    outline="")
    canvas.create_oval(66,526,78,538, fill=GREEN, outline="")
    canvas.create_text(220, 530, fill=MUTED, tags="static",
                       text="chama-auth-lb.log  —  live request stream",
                       font=("Courier", 8))

draw_scene()

# ─── Log system ────────────────────────────────────────────────
log_y   = [544]
log_ids = []

def add_log(text, color=WHITE):
    now = datetime.now().strftime("%H:%M:%S")
    if log_y[0] > H - 56:
        if log_ids:
            canvas.delete(log_ids.pop(0))
            for lid in log_ids:
                canvas.move(lid, 0, -13)
            log_y[0] -= 13
    tid = canvas.create_text(28, log_y[0],
                             text=f"[{now}]  {text}",
                             fill=color, font=("Courier", 7),
                             anchor="w", tags="logline")
    log_ids.append(tid)
    log_y[0] += 13

for t, c in [
    ("AUTH SERVICE  :5000  online  |  JWT validation active", GREEN),
    ("LOAD BALANCER  :5001  online  |  6 services registered", GREEN),
    ("All devices can now send requests.", GREEN),
    ("─"*110, MUTED),
]:
    add_log(t, c)

# ─── Message class ─────────────────────────────────────────────
messages    = []
msg_counter = [0]
total_sent  = [0]
total_auth  = [0]
total_rej   = [0]
paused      = [False]
auto_ms     = [1.0]

class Message:
    def __init__(self, client, name, svc, method, auth_ok):
        self.client   = client
        self.name     = name
        self.svc      = svc
        self.method   = method
        self.auth_ok  = auth_ok
        self.color    = client["color"]
        self.svc_col  = SERVICE_INFO[svc][0]
        self.phase    = "to_auth"
        self.wait     = 0
        self.done     = False
        self.speed    = random.uniform(3.5, 6.5)
        self.trail    = []

        bx, by = CLIENT_BOT[client["id"]]
        self.px = float(bx)
        self.py = float(by)

        self.auth_cx = float(AUTH_X + AUTH_W//2)
        self.auth_cy = float(AUTH_Y + AUTH_H//2)
        self.lb_cx   = float(LB_X + LB_W//2)
        self.lb_cy   = float(LB_Y + LB_H//2)
        sx, sy       = SVC_NODES[svc]
        self.svc_x   = float(sx)
        self.svc_y   = float(sy)

        r = 6
        self.dot = canvas.create_oval(
            self.px-r, self.py-r, self.px+r, self.py+r,
            fill=self.color, outline=WHITE, width=1, tags="msg")
        self.lbl = canvas.create_text(
            self.px, self.py-13, text=name[:14],
            fill=self.color, font=("Courier", 6, "bold"), tags="msg")
        canvas.tag_raise(self.dot)
        canvas.tag_raise(self.lbl)

    def toward(self, tx, ty):
        dx, dy = tx-self.px, ty-self.py
        d = math.hypot(dx, dy)
        if d < self.speed:
            self.px, self.py = tx, ty
            return True
        self.px += (dx/d)*self.speed
        self.py += (dy/d)*self.speed
        return False

    def step(self):
        if self.done:
            return

        if self.phase == "to_auth":
            if self.toward(self.auth_cx, self.auth_cy):
                self.phase = "auth_check"
                self.wait  = 0
                canvas.itemconfig(self.dot, outline=AUTH, width=3)

        elif self.phase == "auth_check":
            self.wait += 1
            if self.wait % 4 == 0:
                r = 6 + (self.wait % 6)
                canvas.coords(self.dot,
                              self.px-r, self.py-r, self.px+r, self.py+r)
            if self.wait > 14:
                canvas.coords(self.dot,
                              self.px-6, self.py-6, self.px+6, self.py+6)
                if not self.auth_ok:
                    canvas.itemconfig(self.dot, fill=RED, outline=RED)
                    canvas.itemconfig(self.lbl, text="401 REJECT", fill=RED)
                    self.phase = "rejected"
                else:
                    canvas.itemconfig(self.dot,
                                      fill=self.svc_col, outline=WHITE, width=1)
                    self.phase = "to_lb"

        elif self.phase == "rejected":
            bx, by = CLIENT_BOT[self.client["id"]]
            if self.toward(bx, by):
                self.done = True
                self.cleanup()

        elif self.phase == "to_lb":
            if self.toward(self.lb_cx, self.lb_cy):
                self.phase = "at_lb"
                self.wait  = 0
                canvas.itemconfig(self.dot, outline=LB, width=2)

        elif self.phase == "at_lb":
            self.wait += 1
            if self.wait > 8:
                canvas.itemconfig(self.dot, outline=WHITE, width=1)
                self.phase = "to_svc"

        elif self.phase == "to_svc":
            if self.toward(self.svc_x, self.svc_y):
                self.phase = "at_svc"
                self.wait  = 0
                canvas.itemconfig(self.dot,
                                  fill=self.svc_col, outline=self.svc_col, width=3)

        elif self.phase == "at_svc":
            self.wait += 1
            if self.wait > 12:
                canvas.itemconfig(self.dot,
                                  fill=self.color, outline=WHITE, width=1)
                canvas.itemconfig(self.lbl, text="200 OK", fill=GREEN)
                self.phase = "return"

        elif self.phase == "return":
            bx, by = CLIENT_BOT[self.client["id"]]
            if self.toward(bx, by):
                self.done = True
                self.cleanup()
                return

        # trail
        if random.random() < 0.45:
            col = RED if self.phase == "rejected" else self.color
            tr  = canvas.create_oval(
                self.px-3, self.py-3, self.px+3, self.py+3,
                fill=col, outline="", tags="trail")
            self.trail.append([tr, 5])

        new_t = []
        for item in self.trail:
            item[1] -= 1
            if item[1] <= 0:
                canvas.delete(item[0])
            else:
                try:
                    co = canvas.coords(item[0])
                    if co:
                        ccx = (co[0]+co[2])/2
                        ccy = (co[1]+co[3])/2
                        r   = item[1]*0.45
                        canvas.coords(item[0], ccx-r, ccy-r, ccx+r, ccy+r)
                    new_t.append(item)
                except:
                    pass
        self.trail = new_t

        r = 6
        canvas.coords(self.dot, self.px-r, self.py-r, self.px+r, self.py+r)
        canvas.coords(self.lbl, self.px, self.py-13)
        canvas.tag_raise(self.dot)
        canvas.tag_raise(self.lbl)

    def cleanup(self):
        canvas.delete(self.dot)
        canvas.delete(self.lbl)
        for item in self.trail:
            canvas.delete(item[0])
        self.trail = []

# ─── Spawn ─────────────────────────────────────────────────────
def spawn(client=None):
    cl   = client or random.choice(CLIENTS)
    mt   = random.choice(MSG_TYPES)
    name, svc, method = mt
    auth_ok = random.random() > 0.15
    total_sent[0] += 1
    if auth_ok:
        total_auth[0] += 1
    else:
        total_rej[0] += 1
    m = Message(cl, name, svc, method, auth_ok)
    messages.append(m)
    col = cl["color"] if auth_ok else RED
    status = "AUTH OK  " if auth_ok else "401 FAIL "
    add_log(
        f"[{cl['id']}] {cl['name']:6}  {cl['sub']:12}  {method:34}  [{status}]",
        col)

def auto_spawn():
    while True:
        time.sleep(auto_ms[0])
        if not paused[0] and len(messages) < 22:
            win.after(0, spawn)

threading.Thread(target=auto_spawn, daemon=True).start()

for i, cl in enumerate(CLIENTS):
    interval = 2.0 + i * 0.6
    def _cl(c=cl, iv=interval):
        while True:
            time.sleep(iv + random.uniform(-0.3, 0.5))
            if not paused[0] and len(messages) < 22:
                win.after(0, lambda cc=c: spawn(cc))
    threading.Thread(target=_cl, daemon=True).start()

# ─── Stats panel ───────────────────────────────────────────────
def draw_stats():
    canvas.delete("stats")
    px, py = 1010, 440
    canvas.create_rectangle(px, py, W-18, py+70,
                            fill=SURFACE, outline=BORDER, width=1, tags="stats")
    canvas.create_text(px+90, py+12, text="LIVE STATS",
                       fill=LB, font=("Courier", 8, "bold"), tags="stats")
    for i, (txt, col) in enumerate([
        (f"Active: {len(messages)}  |  Total: {total_sent[0]}  |  Auth OK: {total_auth[0]}  |  Rejected: {total_rej[0]}", WHITE),
        (f"Status: {'PAUSED ⏸' if paused[0] else 'RUNNING ▶'}", RED if paused[0] else GREEN),
    ]):
        canvas.create_text(px+10, py+28+i*18, text=txt, fill=col,
                           font=("Courier", 7), anchor="w", tags="stats")

    canvas.tag_lower("stats")

def stats_loop():
    draw_stats()
    win.after(250, stats_loop)
win.after(600, stats_loop)

# ─── Animate ───────────────────────────────────────────────────
def animate():
    if not paused[0]:
        for m in messages[:]:
            m.step()
            if m.done:
                try: messages.remove(m)
                except: pass
    win.after(16, animate)

# ─── Controls ──────────────────────────────────────────────────
ctrl = tk.Frame(win, bg=SURFACE)
ctrl.place(x=20, y=H-40, width=700, height=34)

def mk(text, cmd, col=LB):
    return tk.Button(ctrl, text=text, command=cmd, bg=col, fg="#000",
                     font=("Courier", 8, "bold"), relief="flat",
                     padx=10, cursor="hand2")

bp = mk("PAUSE", lambda: None, LB)

def toggle():
    paused[0] = not paused[0]
    bp.config(text="RESUME" if paused[0] else "PAUSE",
              bg=GREEN if paused[0] else LB)

bp.config(command=toggle)
mk("SPEED UP",  lambda: [setattr(auto_ms, 0, max(0.3, auto_ms[0]-0.2)) or
                         [setattr(m, 'speed', min(m.speed+1.5,12)) for m in messages]],
   SAVINGS).pack(side="left", padx=3, pady=5)
bp.pack(side="left", padx=3, pady=5)
mk("SLOW DOWN", lambda: [setattr(auto_ms, 0, min(3.0, auto_ms[0]+0.3)) or
                         [setattr(m, 'speed', max(1.5, m.speed-1.5)) for m in messages]],
   CONTRIB).pack(side="left", padx=3, pady=5)
mk("BURST  (all devices)", lambda: [spawn(cl) for cl in CLIENTS] or [spawn() for _ in range(4)],
   NOTIF).pack(side="left", padx=3, pady=5)
mk("CLEAR", lambda: [m.cleanup() or messages.clear() or add_log("[CTRL] Cleared", RED)],
   LOAN).pack(side="left", padx=3, pady=5)

canvas.create_text(20, H-6,
                   text="Controls: SPEED UP  ·  PAUSE  ·  SLOW DOWN  ·  BURST  ·  CLEAR",
                   fill=MUTED, font=("Courier", 7), anchor="w", tags="static")

animate()
win.mainloop()