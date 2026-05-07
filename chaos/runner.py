import argparse
import time
import requests


BASE_URL = "http://127.0.0.1:8000"


def start_chaos(failure_rate: float, latency_ms: int):
    response = requests.post(
        f"{BASE_URL}/chaos/start",
        params={
            "failure_rate": failure_rate,
            "latency_ms": latency_ms,
        },
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

    print(f"Running {iterations} probes against /api/data...")

    for i in range(1, iterations + 1):
        try:
            start = time.time()
            response = requests.get(f"{BASE_URL}/api/data", timeout=10)
            elapsed_ms = round((time.time() - start) * 1000, 2)

            if response.status_code == 200:
                success += 1
                print(f"[{i}] PASS {response.status_code} {elapsed_ms}ms")
            else:
                failures += 1
                print(f"[{i}] FAIL {response.status_code} {elapsed_ms}ms")

        except requests.RequestException as error:
            failures += 1
            print(f"[{i}] ERROR {error}")

        time.sleep(delay)

    print("\nExperiment Summary")
    print("------------------")
    print(f"Total probes: {iterations}")
    print(f"Successes: {success}")
    print(f"Failures: {failures}")
    print(f"Failure rate observed: {round((failures / iterations) * 100, 2)}%")


def run_experiment(failure_rate: float, latency_ms: int, iterations: int, delay: float):
    try:
        start_chaos(failure_rate, latency_ms)
        run_probe(iterations, delay)
    finally:
        stop_chaos()


def main():
    parser = argparse.ArgumentParser(description="Cloud Chaos Lab Runner")

    parser.add_argument("--failure-rate", type=float, default=0.5)
    parser.add_argument("--latency-ms", type=int, default=500)
    parser.add_argument("--iterations", type=int, default=20)
    parser.add_argument("--delay", type=float, default=0.2)

    args = parser.parse_args()

    run_experiment(
        failure_rate=args.failure_rate,
        latency_ms=args.latency_ms,
        iterations=args.iterations,
        delay=args.delay,
    )


if __name__ == "__main__":
    main()