#!/bin/bash
# Script that tests the app's endpoints
DATA_WINDOW_HOURS=0.1
export DATA_WINDOW_HOURS

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEST_DATA_FILE="$SCRIPT_DIR/test_files/data.json"

curl -X POST http://localhost:5000/

curl -X POST http://localhost:5000/extract_data

curl -X POST http://127.0.0.1:5000/process-and-load-data -H "Content-Type: application/json" -d @"$TEST_DATA_FILE"
