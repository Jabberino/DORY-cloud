#!/bin/bash

HOST="ccscloud.dlsu.edu.ph"
PORT="11526"
URL="http://$HOST:$PORT/metrics/upload_csv"
CSV_FILE="test_data.csv"

# Generate CSV if missing
if [ ! -f "$CSV_FILE" ]; then
    echo "Generating test data..."
    python3 scripts/generate_csv.py
fi

echo "---------------------------------------------------"
echo "Testing Remote API: $URL"
echo "Uploading $CSV_FILE..."
echo "---------------------------------------------------"

# Run curl
# -s: Silent
# -w: Write custom output (http_code)
# -o: Output response to file
response=$(curl -s -w "%{http_code}" -o response_remote.json -F "file=@$CSV_FILE" "$URL")

if [ "$response" -eq 200 ]; then
    echo "SUCCESS! (HTTP 200)"
    echo "Response preview:"
    head -n 20 response_remote.json
else
    echo "FAILED. HTTP Status: $response"
    echo "Response body:"
    cat response_remote.json
fi
echo ""
