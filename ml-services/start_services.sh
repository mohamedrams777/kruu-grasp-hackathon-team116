#!/bin/bash

echo "Starting all ML services..."

# Start emotion service
echo "Starting emotion detection service on port 8001..."
python emotion_service.py &
EMOTION_PID=$!

# Start intent service
echo "Starting intent classification service on port 8002..."
python intent_service.py &
INTENT_PID=$!

# Start RAG service
echo "Starting RAG truth verification service on port 8003..."
python rag_service.py &
RAG_PID=$!

echo ""
echo "✅ All services started!"
echo "Emotion Detection: http://localhost:8001"
echo "Intent Classification: http://localhost:8002"
echo "RAG Verification: http://localhost:8003"
echo ""
echo "Press Ctrl+C to stop all services..."

# Wait for any process to exit
wait -n

# Kill all background jobs
kill $EMOTION_PID $INTENT_PID $RAG_PID 2>/dev/null
