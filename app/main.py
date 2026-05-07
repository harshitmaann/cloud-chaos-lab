import random
import time
from fastapi import FastAPI, Response
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

app = FastAPI(title="Cloud Chaos Lab Target App")

REQUEST_COUNT = Counter("app_requests_total", "Total requests received")
FAILURE_COUNT = Counter("app_failures_total", "Total simulated failures")
LATENCY = Histogram("app_request_latency_seconds", "Request latency")

CHAOS_MODE = {
    "enabled": False,
    "failure_rate": 0.0,
    "latency_ms": 0
}


@app.get("/")
def root():
    return {"message": "Cloud Chaos Lab target app is running"}


@app.get("/health")
def health():
    return {"status": "healthy", "chaos": CHAOS_MODE}


@app.get("/api/data")
def get_data():
    REQUEST_COUNT.inc()

    with LATENCY.time():
        if CHAOS_MODE["latency_ms"] > 0:
            time.sleep(CHAOS_MODE["latency_ms"] / 1000)

        if CHAOS_MODE["enabled"] and random.random() < CHAOS_MODE["failure_rate"]:
            FAILURE_COUNT.inc()
            return Response(
                content='{"error": "simulated upstream failure"}',
                media_type="application/json",
                status_code=503
            )

        return {
            "data": "important production response",
            "chaos_enabled": CHAOS_MODE["enabled"]
        }


@app.post("/chaos/start")
def start_chaos(failure_rate: float = 0.5, latency_ms: int = 500):
    CHAOS_MODE["enabled"] = True
    CHAOS_MODE["failure_rate"] = failure_rate
    CHAOS_MODE["latency_ms"] = latency_ms

    return {
        "message": "chaos started",
        "failure_rate": failure_rate,
        "latency_ms": latency_ms
    }


@app.post("/chaos/stop")
def stop_chaos():
    CHAOS_MODE["enabled"] = False
    CHAOS_MODE["failure_rate"] = 0.0
    CHAOS_MODE["latency_ms"] = 0

    return {"message": "chaos stopped"}


@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)