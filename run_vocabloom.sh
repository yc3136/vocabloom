#!/bin/bash

# Start backend
cd server
./run_server.sh &
BACKEND_PID=$!
cd ..

# Start frontend
cd client
npm run dev &
FRONTEND_PID=$!
cd ..

# Print info
sleep 2
echo "Backend running on http://127.0.0.1:8000 (PID: $BACKEND_PID)"
echo "Frontend running on http://localhost:5173 (PID: $FRONTEND_PID)"
echo "To stop both, run: kill $BACKEND_PID $FRONTEND_PID" 