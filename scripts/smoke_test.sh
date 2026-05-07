#!/bin/bash

echo "Running smoke test..."

STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/health)

if [ "$STATUS" = "200" ]; then
  echo "PASS: App health endpoint is reachable"
  exit 0
else
  echo "FAIL: App health endpoint returned $STATUS"
  exit 1
fi