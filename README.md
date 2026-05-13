# Cloud Chaos Lab

A chaos engineering lab for simulating production failures, validating automated recovery workflows, and visualizing system health using Prometheus and Grafana.

## Features

- FastAPI production-style API service
- Chaos injection endpoints
- Latency and failure simulation
- Automated chaos experiment runner
- Dockerized multi-service architecture
- Container failure injection and recovery
- Prometheus metrics collection
- Grafana observability dashboards
- JSON experiment report generation

## Architecture

```text
                +-------------------+
                |   Chaos Runner    |
                +---------+---------+
                          |
                          v
+------------+     +-------------+     +----------------+
| Prometheus |<----| API Service |---->| Backend Service|
+------------+     +-------------+     +----------------+
       |
       v
+-------------+
|   Grafana   |
+-------------+
```

## Tech Stack

- Python
- FastAPI
- Docker
- Prometheus
- Grafana
- Requests
- Docker SDK for Python

## Chaos Scenarios

### Latency Injection

```bash
python -m chaos.runner \
  --failure-rate 0.7 \
  --latency-ms 1200 \
  --iterations 20
```

### Container Failure Simulation

```bash
python -m chaos.runner \
  --kill-container backend-service
```

## Observability

Prometheus scrapes application metrics every 5 seconds.

Grafana visualizes:
- request throughput
- latency spikes
- service health
- chaos experiment activity

## Example Metrics

- `app_requests_total`
- `app_failures_total`
- `app_request_latency_seconds`

## Local Setup

### Start services

```bash
docker compose up --build
```

### API

```text
http://127.0.0.1:8000
```

### Prometheus

```text
http://127.0.0.1:9090
```

### Grafana

```text
http://127.0.0.1:3000
```

## Future Improvements

- Kubernetes chaos scenarios
- Alertmanager integration
- Slack incident notifications
- Automated rollback workflows
- Distributed tracing
- Network partition simulation
- Load testing integration

## Why I Built This

I wanted to better understand how production systems behave during failure conditions — not just how applications run normally.

This project explores:
- resilience engineering
- observability
- operational recovery
- distributed systems behavior
- platform reliability workflows