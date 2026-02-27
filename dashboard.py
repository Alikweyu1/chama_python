"""
CHAMA Microservices Live Dashboard
Real-time visual monitoring of all services and load balancer.
"""
import tkinter as tk
from tkinter import font as tkfont
import urllib.request
import json
import threading
import time
from datetime import datetime

SERVICES = {
    "Load Balancer":  {"url": "http://localhost:5000/health", "port": 5000, "color": "#F39C12"},
    "Member":         {"url": "http://localhost:5001/health", "port": 5001, "color": "#3498DB"},
    "Contribution":   {"url": "http://localhost:5002/health", "port": 5002, "color": "#2ECC71"},
    "Loan":           {"url": "http://localhost:5003/health", "port": 5003, "color": "#E74C3C"},
    "Notification":   {"url": "http://localhost:5004/health", "port": 5004, "color": "#9B59B6"},
    "Savings":        {"url": "http://localhost:5005/health", "port": 5005, "color": "#1ABC9C"},
    "Report":         {"url": "http://localhost:5006/health", "port": 5006, "color": "#E67E22"},
}

window = tk.Tk()
window.title("🏦 Chama Microservices Dashboard")
window.geometry("950x680")
window.configure(bg="#0d1117")
window.resizable(True, True)

BG     = "#0d1117"
CARD   = "#161b22"
BORDER = "#30363d"
GREEN  = "#2ECC71"
RED    = "#E74C3C"
YELLOW = "#F39C12"
WHITE  = "#e6edf3"
GRAY   = "#8b949e"

# ─── Header ────────────────────────────────────────────────────
hdr = tk.Frame(window, bg="#161b22", pady=12)
hdr.pack(fill="x", padx=0)

tk.Label(hdr, text="🏦  CHAMA MICROSERVICES DASHBOARD",
         font=("Arial", 16, "bold"), bg="#161b22", fg=WHITE).pack(side="left", padx=20)

clock_lbl = tk.Label(hdr, text="", font=("Arial", 11), bg="#161b22", fg=GRAY)
clock_lbl.pack(side="right", padx=20)

# ─── Stats bar ─────────────────────────────────────────────────
stats_bar = tk.Frame(window, bg=BG)
stats_bar.pack(fill="x", padx=16, pady=(8,4))

stat_vals = {}
for title, key in [("Total Requests","requests"), ("Successful","success"), ("Failed","failed"), ("Services Up","up")]:
    f = tk.Frame(stats_bar, bg=CARD, padx=16, pady=8, relief="flat")
    f.pack(side="left", padx=6, expand=True, fill="x")
    tk.Label(f, text=title, font=("Arial", 9), bg=CARD, fg=GRAY).pack()
    lbl = tk.Label(f, text="—", font=("Arial", 18, "bold"), bg=CARD, fg=WHITE)
    lbl.pack()
    stat_vals[key] = lbl

# ─── Service cards ─────────────────────────────────────────────
cards_frame = tk.Frame(window, bg=BG)
cards_frame.pack(fill="both", expand=True, padx=16, pady=4)

service_widgets = {}

def make_card(parent, name, info, row, col):
    frame = tk.Frame(parent, bg=CARD, padx=14, pady=10, relief="flat",
                     highlightbackground=BORDER, highlightthickness=1)
    frame.grid(row=row, column=col, padx=6, pady=6, sticky="nsew")

    top = tk.Frame(frame, bg=CARD)
    top.pack(fill="x")

    dot = tk.Label(top, text="●", font=("Arial", 14), bg=CARD, fg=GRAY)
    dot.pack(side="left", padx=(0,6))

    tk.Label(top, text=name, font=("Arial", 12, "bold"), bg=CARD, fg=WHITE).pack(side="left")

    port_lbl = tk.Label(top, text=f":{info['port']}", font=("Arial", 10), bg=CARD, fg=GRAY)
    port_lbl.pack(side="right")

    status_lbl = tk.Label(frame, text="Checking...", font=("Arial", 10), bg=CARD, fg=GRAY)
    status_lbl.pack(anchor="w", pady=(4,0))

    ping_lbl = tk.Label(frame, text="", font=("Arial", 9), bg=CARD, fg=GRAY)
    ping_lbl.pack(anchor="w")

    bar_bg = tk.Frame(frame, bg=BORDER, height=4)
    bar_bg.pack(fill="x", pady=(6,0))
    bar_fill = tk.Frame(bar_bg, bg=info["color"], height=4, width=0)
    bar_fill.place(x=0, y=0, relheight=1)

    service_widgets[name] = {
        "dot": dot, "status": status_lbl,
        "ping": ping_lbl, "bar": bar_fill,
        "frame": frame, "color": info["color"]
    }

for col in range(4):
    cards_frame.columnconfigure(col, weight=1)

names = list(SERVICES.keys())
for i, name in enumerate(names):
    make_card(cards_frame, name, SERVICES[name], i // 4, i % 4)

# ─── Log panel ─────────────────────────────────────────────────
log_frame = tk.Frame(window, bg=CARD, highlightbackground=BORDER, highlightthickness=1)
log_frame.pack(fill="both", expand=True, padx=16, pady=(4,12))

tk.Label(log_frame, text="  📋 Live Request Log", font=("Arial", 10, "bold"),
         bg=CARD, fg=WHITE, anchor="w").pack(fill="x", pady=(6,2), padx=4)

log_text = tk.Text(log_frame, height=8, bg="#0d1117", fg=GREEN,
                   font=("Courier New", 9), relief="flat", insertbackground=GREEN,
                   selectbackground="#30363d")
log_text.pack(fill="both", expand=True, padx=4, pady=(0,4))
log_text.config(state="disabled")

log_colors = {
    "UP":    GREEN,
    "DOWN":  RED,
    "WARN":  YELLOW,
    "INFO":  "#58a6ff",
}

def log(msg, level="INFO"):
    now = datetime.now().strftime("%H:%M:%S")
    color = log_colors.get(level, WHITE)
    log_text.config(state="normal")
    log_text.insert("end", f"[{now}] ", "time")
    log_text.insert("end", f"[{level}] ", level)
    log_text.insert("end", f"{msg}\n")
    log_text.tag_config("time", foreground=GRAY)
    log_text.tag_config(level, foreground=color)
    log_text.see("end")
    log_text.config(state="disabled")

# ─── Health check ──────────────────────────────────────────────
lb_data   = {}
up_count  = 0
req_total = 0
req_ok    = 0
req_fail  = 0

def check_service(name, info):
    global up_count
    t0 = time.time()
    try:
        req = urllib.request.Request(info["url"], method="GET")
        with urllib.request.urlopen(req, timeout=3) as resp:
            data = json.loads(resp.read())
            ms   = round((time.time()-t0)*1000, 1)
            return True, ms, data
    except:
        ms = round((time.time()-t0)*1000, 1)
        return False, ms, {}

def refresh():
    global up_count, req_total, req_ok, req_fail, lb_data
    up_count = 0

    for name, info in SERVICES.items():
        ok, ms, data = check_service(name, info)
        w = service_widgets[name]

        if ok:
            up_count += 1
            w["dot"].config(fg=GREEN)
            w["status"].config(text="● ONLINE", fg=GREEN)
            w["ping"].config(text=f"Response: {ms}ms", fg=GRAY)
            # Animate bar based on response time
            bar_w = max(10, min(300, int(300 - ms * 2)))
            w["bar"].config(width=bar_w, bg=info["color"])
            if name == "Load Balancer" and data:
                lb_data = data
                req_total = data.get("metrics",{}).get("total_requests",0)
                req_ok    = data.get("metrics",{}).get("successful",0)
                req_fail  = data.get("metrics",{}).get("failed",0)
                svc_status = data.get("services",{})
                log(f"LB healthy | Requests: {req_total} | Services: {len(svc_status)} registered", "UP")
        else:
            w["dot"].config(fg=RED)
            w["status"].config(text="● OFFLINE", fg=RED)
            w["ping"].config(text=f"Timeout: {ms}ms", fg=RED)
            w["bar"].config(width=10, bg=RED)
            log(f"{name} is DOWN on port {info['port']}", "DOWN")

    # Update stats bar
    stat_vals["requests"].config(text=str(req_total) if req_total else "—")
    stat_vals["success"].config(text=str(req_ok)    if req_ok    else "—")
    stat_vals["failed"].config(text=str(req_fail)   if req_fail  else "—", fg=RED if req_fail else WHITE)
    stat_vals["up"].config(text=f"{up_count}/{len(SERVICES)}", fg=GREEN if up_count==len(SERVICES) else YELLOW)

    clock_lbl.config(text=datetime.now().strftime("Last updated: %H:%M:%S"))
    window.after(5000, refresh)

# ─── Simulate some traffic ─────────────────────────────────────
SAMPLE_CALLS = [
    ("GET", "http://localhost:5000/members",             "Fetching member list"),
    ("GET", "http://localhost:5000/contributions/summary","Contribution summary"),
    ("GET", "http://localhost:5000/loans/summary",        "Loan summary"),
    ("GET", "http://localhost:5000/savings",              "Savings balance"),
    ("GET", "http://localhost:5000/reports/financial-summary","Financial report"),
    ("GET", "http://localhost:5000/notifications",        "Recent notifications"),
    ("GET", "http://localhost:5000/portfolio",            "Investment portfolio"),
]

call_idx = [0]

def simulate_traffic():
    while True:
        time.sleep(8)
        url_method, url, label = SAMPLE_CALLS[call_idx[0] % len(SAMPLE_CALLS)]
        call_idx[0] += 1
        t0 = time.time()
        try:
            req = urllib.request.Request(url, method=url_method)
            with urllib.request.urlopen(req, timeout=4) as resp:
                ms  = round((time.time()-t0)*1000,1)
                svc = resp.headers.get("X-Served-By","?")
                window.after(0, lambda l=label, m=ms, s=svc: log(f"{l} → served by [{s}] in {m}ms","INFO"))
        except Exception as e:
            window.after(0, lambda e=e: log(f"Traffic error: {e}","WARN"))

threading.Thread(target=simulate_traffic, daemon=True).start()

log("Dashboard started. Checking services...", "INFO")
log("Load balancer on port 5000 | Services on 5001-5006", "INFO")
log("Run: python run_all.py to start all services", "INFO")
log("─" * 60, "INFO")

window.after(500, refresh)
window.mainloop()
