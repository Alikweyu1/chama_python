"""
CHAMA Microservices — Master Launcher
Starts all 6 services + load balancer in separate processes.
"""
import subprocess
import sys
import time
import os
import signal
import urllib.request

BASE = os.path.dirname(os.path.abspath(__file__))

SERVICES = [
    ("Member Service",        os.path.join(BASE, "services", "member_service.py"),       5001),
    ("Contribution Service",  os.path.join(BASE, "services", "contribution_service.py"), 5002),
    ("Loan Service",          os.path.join(BASE, "services", "loan_service.py"),         5003),
    ("Notification Service",  os.path.join(BASE, "services", "notification_service.py"), 5004),
    ("Savings Service",       os.path.join(BASE, "services", "savings_service.py"),      5005),
    ("Report Service",        os.path.join(BASE, "services", "report_service.py"),       5006),
    ("Load Balancer",         os.path.join(BASE, "load_balancer.py"),                    5000),
]

procs = []

def start_all():
    print("\n" + "="*55)
    print("  🏦  CHAMA MICROSERVICES SYSTEM")
    print("="*55)

    for name, path, port in SERVICES:
        print(f"  Starting {name} on port {port}...", end=" ", flush=True)
        p = subprocess.Popen(
            [sys.executable, path],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        procs.append(p)
        time.sleep(0.8)
        print("✓")

    print("="*55)
    print("  ✅ All services started!")
    print()
    print("  ENDPOINTS (via Load Balancer on :5000):")
    print("  ─────────────────────────────────────────")
    print("  GET  /members                 → Member list")
    print("  POST /members                 → Register member")
    print("  GET  /contributions/summary   → Contribution totals")
    print("  POST /contributions           → Record contribution")
    print("  GET  /loans/summary           → Loan summary")
    print("  POST /loans                   → Apply for loan")
    print("  GET  /notifications           → View notifications")
    print("  POST /notifications/broadcast → Send to all")
    print("  GET  /savings                 → Savings pool")
    print("  GET  /investments             → Investments")
    print("  GET  /portfolio               → Full portfolio")
    print("  GET  /reports/financial-summary → Financial report")
    print("  GET  /services                → LB service registry")
    print("  GET  /health                  → LB health check")
    print("="*55)

    # Wait for services to warm up
    time.sleep(2)
    print("\n  🏃 Checking service health...")
    all_ok = True
    for name, _, port in SERVICES:
        try:
            with urllib.request.urlopen(f"http://localhost:{port}/health", timeout=3) as r:
                status = "✅ UP" if r.status == 200 else "⚠️  WARN"
        except:
            status = "❌ DOWN"
            all_ok = False
        print(f"  {name:28} Port {port}  {status}")

    print()
    if all_ok:
        print("  🎉 All services healthy! System is ready.")
    else:
        print("  ⚠️  Some services may still be starting up.")

    print("\n  📊 Opening Dashboard...")
    print("  Press Ctrl+C to stop all services.\n")

    try:
        subprocess.run([sys.executable, os.path.join(BASE, "dashboard.py")])
    except KeyboardInterrupt:
        pass

def stop_all(sig=None, frame=None):
    print("\n\n  Shutting down all services...")
    for p in procs:
        try:
            p.terminate()
        except:
            pass
    print("  All services stopped. Goodbye!")
    sys.exit(0)

signal.signal(signal.SIGINT, stop_all)

if __name__ == "__main__":
    start_all()
    stop_all()
