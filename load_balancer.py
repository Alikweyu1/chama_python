"""
CHAMA Load Balancer — Port 5000
Round-robin load balancer that distributes requests across all microservices.
"""
from flask import Flask, jsonify, request, Response
import urllib.request
import urllib.error
import json
import time
import threading
from datetime import datetime
from collections import defaultdict

app = Flask(__name__)

# ─── Service Registry ──────────────────────────────────────────
SERVICES = {
    "member":       {"instances": ["http://localhost:5001"], "index": 0, "healthy": [True]},
    "contribution": {"instances": ["http://localhost:5002"], "index": 0, "healthy": [True]},
    "loan":         {"instances": ["http://localhost:5003"], "index": 0, "healthy": [True]},
    "notification": {"instances": ["http://localhost:5004"], "index": 0, "healthy": [True]},
    "savings":      {"instances": ["http://localhost:5005"], "index": 0, "healthy": [True]},
    "report":       {"instances": ["http://localhost:5006"], "index": 0, "healthy": [True]},
}

SERVICE_ROUTES = {
    "member":       ["/members"],
    "contribution": ["/contributions"],
    "loan":         ["/loans"],
    "notification": ["/notifications"],
    "savings":      ["/savings", "/investments", "/dividends", "/portfolio"],
    "report":       ["/reports"],
}

# ─── Metrics ───────────────────────────────────────────────────
metrics = {
    "total_requests":   0,
    "successful":       0,
    "failed":           0,
    "requests_per_svc": defaultdict(int),
    "response_times":   defaultdict(list),
    "start_time":       datetime.now().isoformat()
}
lock = threading.Lock()

def get_next_instance(service_name):
    """Round-robin selection"""
    svc = SERVICES[service_name]
    idx = svc["index"] % len(svc["instances"])
    svc["index"] = (idx + 1) % len(svc["instances"])
    return svc["instances"][idx]

def forward_request(target_url, method, headers, body):
    try:
        req_headers = {k: v for k, v in headers.items()
                       if k.lower() not in ("host","content-length")}
        req = urllib.request.Request(target_url, data=body, headers=req_headers, method=method)
        with urllib.request.urlopen(req, timeout=5) as resp:
            return resp.read(), resp.status, dict(resp.headers)
    except urllib.error.HTTPError as e:
        return e.read(), e.code, {}
    except Exception as e:
        return json.dumps({"error": str(e)}).encode(), 503, {}

def detect_service(path):
    for svc, routes in SERVICE_ROUTES.items():
        for route in routes:
            if path.startswith(route):
                return svc
    return None

# ─── Health checker ────────────────────────────────────────────
def health_check_loop():
    while True:
        for name, svc in SERVICES.items():
            for i, url in enumerate(svc["instances"]):
                try:
                    req = urllib.request.Request(f"{url}/health", method="GET")
                    with urllib.request.urlopen(req, timeout=2):
                        svc["healthy"][i] = True
                except:
                    svc["healthy"][i] = False
        time.sleep(10)

threading.Thread(target=health_check_loop, daemon=True).start()

# ─── Routes ────────────────────────────────────────────────────
@app.route("/health")
def lb_health():
    svc_status = {}
    for name, svc in SERVICES.items():
        svc_status[name] = {
            "instances": len(svc["instances"]),
            "healthy":   sum(svc["healthy"]),
            "urls":      svc["instances"]
        }
    return jsonify({
        "service": "Chama Load Balancer",
        "status":  "UP",
        "port":    5000,
        "services": svc_status,
        "metrics": {
            "total_requests": metrics["total_requests"],
            "successful":     metrics["successful"],
            "failed":         metrics["failed"],
            "requests_per_service": dict(metrics["requests_per_svc"]),
            "uptime_since":   metrics["start_time"]
        }
    })

@app.route("/services")
def list_services():
    result = {}
    for name, svc in SERVICES.items():
        result[name] = {
            "instances": svc["instances"],
            "healthy":   svc["healthy"],
            "routes":    SERVICE_ROUTES[name],
            "requests":  metrics["requests_per_svc"][name]
        }
    return jsonify({"success": True, "load_balancer": "Round-Robin", "services": result})

@app.route("/<path:path>", methods=["GET","POST","PUT","DELETE"])
def proxy(path):
    full_path = "/" + path
    svc_name  = detect_service(full_path)

    with lock:
        metrics["total_requests"] += 1

    if not svc_name:
        return jsonify({"error": f"No service found for path: {full_path}",
                        "available_paths": list(SERVICE_ROUTES.keys())}), 404

    base_url    = get_next_instance(svc_name)
    query       = request.query_string.decode()
    target_url  = f"{base_url}{full_path}" + (f"?{query}" if query else "")
    body        = request.get_data() or None
    start       = time.time()

    data, status, resp_headers = forward_request(target_url, request.method, dict(request.headers), body)
    elapsed = round((time.time() - start) * 1000, 2)

    with lock:
        metrics["requests_per_svc"][svc_name] += 1
        metrics["response_times"][svc_name].append(elapsed)
        if status < 400:
            metrics["successful"] += 1
        else:
            metrics["failed"] += 1

    print(f"[LB] {request.method} {full_path} → {svc_name} ({base_url}) | {status} | {elapsed}ms")

    content_type = resp_headers.get("Content-Type","application/json")
    return Response(data, status=status, content_type=content_type,
                    headers={"X-Served-By": svc_name,
                             "X-Response-Time": f"{elapsed}ms",
                             "X-Load-Balancer": "Chama-LB-v1"})

if __name__ == "__main__":
    print("=" * 55)
    print("  CHAMA MICROSERVICES LOAD BALANCER")
    print("  Listening on http://localhost:5000")
    print("  Strategy: Round-Robin")
    print("=" * 55)
    for name, routes in SERVICE_ROUTES.items():
        print(f"  {name:15} → {', '.join(routes)}")
    print("=" * 55)
    app.run(port=5000, debug=False)
