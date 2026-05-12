import argparse
import json
import time
from datetime import datetime
from pathlib import Path

import docker
import requests


BASE_URL = "http://127.0.0.1:8000"


def start_chaos(failure_rate: float, latency_ms: int):
    response = requests.post(
        f"{BASE_URL}/chaos/start",
        params={"failure_rate": failure_rate, "latency_ms": latency_ms},
        timeout=5,
    )
    response.raise_for_status()
    print("Chaos started:", response.json())


def stop_chaos():
    response = requests.post(f"{BASE_URL}/chaos/stop", timeout=5)
    response.raise_for_status()
    print("Chaos stopped:", response.json())


def run_probe(iterations: int, delay: float):
    success = 0
    failures = 0
    results = []

    print(f"Running {iterations} probes against /api/data...")

    for i in range(1, iterations + 1):
        try:
            start = time.time()
            response = requests.get(f"{BASE_URL}/api/data", timeout=10)
            elapsed_ms = round((time.time() - start) * 1000, 2)

            if response.status_code == 200:
                success += 1
                status = "PASS"
            else:
                failures += 1
                status = "FAIL"

            print(f"[{i}] {status} {response.status_code} {elapsed_ms}ms")

            results.append(
                {
                    "probe": i,
                    "status": status,
                    "status_code": response.status_code,
                    "latency_ms": elapsed_ms,
                }
            )

        except requests.RequestException as error:
            failures += 1
            print(f"[{i}] ERROR {error}")

            results.append(
                {
                    "probe": i,
                    "status": "ERROR",
                    "status_code": None,
                    "latency_ms": None,
                    "error": str(error),
                }
            )

        time.sleep(delay)

    print("\nExperiment Summary")
    print("------------------")
    print(f"Total probes: {iterations}")
    print(f"Successes: {success}")
    print(f"Failures: {failures}")
    print(f"Failure rate observed: {round((failures / iterations) * 100, 2)}%")

    report = {
        "timestamp": datetime.utcnow().isoformat(),
        "iterations": iterations,
        "successes": success,
        "failures": failures,
        "failure_rate_percent": round((failures / iterations) * 100, 2),
        "results": results,
    }

    reports_dir = Path("reports")
    reports_dir.mkdir(exist_ok=True)

    filename = f"chaos_report_{int(time.time())}.json"
    report_path = reports_dir / filename

    with open(report_path, "w") as file:
        json.dump(report, file, indent=2)

    print(f"\nReport saved to: {report_path}")


def run_experiment(failure_rate: float, latency_ms: int, iterations: int, delay: float):
    try:
        start_chaos(failure_rate, latency_ms)
        run_probe(iterations, delay)
    finally:
        stop_chaos()


def kill_container(container_name: str):
    client = docker.from_env()
    container = client.containers.get(container_name)
    container.reload()

    print(f"Target container: {container_name}")
    print(f"Initial status: {container.status}")

    if container.status == "running":
        print(f"Injecting failure by killing container: {container_name}")
        container.kill()
        print("Waiting 3 seconds after failure injection...")
        time.sleep(3)
    else:
        print(f"Container is not running, skipping kill step: {container.status}")

    container.reload()
    print(f"Status after failure window: {container.status}")

    if container.status != "running":
        print(f"Recovering container: {container_name}")
        container.start()

    print("Waiting for recovery verification...")
    time.sleep(5)

    container.reload()
    print(f"Container status after recovery window: {container.status}")

    if container.status == "running":
        print("Recovery verified: PASS")
    else:
        print("Recovery verified: FAIL")
def main():
    parser = argparse.ArgumentParser(description="Cloud Chaos Lab Runner")
    parser.add_argument("--failure-rate", type=float, default=0.5)
    parser.add_argument("--latency-ms", type=int, default=500)
    parser.add_argument("--iterations", type=int, default=20)
    parser.add_argument("--delay", type=float, default=0.2)
    parser.add_argument("--kill-container", type=str, default=None)

    args = parser.parse_args()

    if args.kill_container:
        kill_container(args.kill_container)
    else:
        run_experiment(
            failure_rate=args.failure_rate,
            latency_ms=args.latency_ms,
            iterations=args.iterations,
            delay=args.delay,
        )


if __name__ == "__main__":
    main()