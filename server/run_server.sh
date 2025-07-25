#!/bin/bash

PORT=8000
PID=$(lsof -ti :$PORT)
if [ -n "$PID" ]; then
  echo "Port $PORT is in use by PID $PID. Killing..."
  kill -9 $PID
fi

# Start the FastAPI server
poetry run uvicorn vocabloom_server.main:app --reload --port $PORT 