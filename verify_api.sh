#!/bin/bash

# Ensure Docker is running
if ! docker info > /dev/null 2>&1; then
  echo "Docker is not running. Please start Docker and try again."
  exit 1
fi

echo "Starting API..."
docker-compose up -d --build

echo "Waiting for API to be ready..."
sleep 5

echo "Sending test request..."
curl -X POST "http://localhost:8000/metrics/session" \
     -H "Content-Type: application/json" \
     -d @test_payload.json > response.json

echo ""
echo "Response saved to response.json"
cat response.json | head -n 20
echo "..."
