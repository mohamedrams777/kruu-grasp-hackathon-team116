# Start all ML microservices in background

Write-Host "Starting ML Microservices..." -ForegroundColor Cyan
Write-Host ""

# Start Emotion Detection Service (Port 8001)
Write-Host "[1/6] Starting Emotion Detection Service (Port 8001)..." -ForegroundColor Yellow
Start-Process python -ArgumentList "emotion_service.py" -NoNewWindow -RedirectStandardOutput "emotion_service_out.log" -RedirectStandardError "emotion_service_err.log"

# Start Intent Classification Service (Port 8002)
Write-Host "[2/6] Starting Intent Classification Service (Port 8002)..." -ForegroundColor Yellow
Start-Process python -ArgumentList "intent_service.py" -NoNewWindow -RedirectStandardOutput "intent_service_out.log" -RedirectStandardError "intent_service_err.log"

# Start RAG Truth Verification Service (Port 8003)
Write-Host "[3/6] Starting RAG Truth Verification Service (Port 8003)..." -ForegroundColor Yellow
Start-Process python -ArgumentList "rag_service.py" -NoNewWindow -RedirectStandardOutput "rag_service_out.log" -RedirectStandardError "rag_service_err.log"

# Start CNN-BERT Harm Detection Service (Port 8004)
Write-Host "[4/6] Starting CNN-BERT Harm Detection Service (Port 8004)..." -ForegroundColor Yellow
Start-Process python -ArgumentList "cnn_bert_service.py" -NoNewWindow -RedirectStandardOutput "cnn_service_out.log" -RedirectStandardError "cnn_service_err.log"

# Start LLM Chatbot Service (Port 8005)
Write-Host "[5/6] Starting LLM Chatbot Service (Port 8005)..." -ForegroundColor Yellow
Start-Process python -ArgumentList "llm_chatbot_service.py" -NoNewWindow -RedirectStandardOutput "llm_service_out.log" -RedirectStandardError "llm_service_err.log"

# Start Time-Series Analysis Service (Port 8006)
Write-Host "[6/6] Starting Time-Series Analysis Service (Port 8006)..." -ForegroundColor Yellow
Start-Process python -ArgumentList "timeseries_service.py" -NoNewWindow -RedirectStandardOutput "timeseries_service_out.log" -RedirectStandardError "timeseries_service_err.log"

Write-Host ""
Write-Host "All 6 services started!" -ForegroundColor Green
Write-Host ""
Write-Host "Services running on:" -ForegroundColor Cyan
Write-Host "  - Emotion Detection:    http://localhost:8001" -ForegroundColor White
Write-Host "  - Intent Classification: http://localhost:8002" -ForegroundColor White
Write-Host "  - RAG Verification:      http://localhost:8003" -ForegroundColor White
Write-Host "  - CNN-BERT Harm:         http://localhost:8004" -ForegroundColor White
Write-Host "  - LLM Chatbot:           http://localhost:8005" -ForegroundColor White
Write-Host "  - Time-Series Analysis:  http://localhost:8006" -ForegroundColor White
Write-Host ""
Write-Host "⏳ Waiting for models to load (this may take 30-90 seconds)..." -ForegroundColor Yellow
Write-Host "Check logs: Get-Content *_out.log,*_err.log -Wait" -ForegroundColor Gray
Write-Host ""
Write-Host "To stop all services: Get-Process python | Stop-Process" -ForegroundColor Gray
