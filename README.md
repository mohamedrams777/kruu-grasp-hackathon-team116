Harm-Based Misinformation Detection System - Implementation Walkthrough
🎉 Project Complete
Successfully implemented a fully functional MVP of a harm-based misinformation detection system that analyzes statements for potential harm using AI-powered multi-dimensional analysis.

✅ What Was Built
1. Frontend Application (React + TypeScript)
Main Components Created
ChatInterface.tsx

Main user interface with textarea input
Submit button with loading states
Results display grid layout
Error handling and messaging
Placeholder "How It Works" guide
RiskMeter.tsx

Animated SVG circular progress indicator (0-100 scale)
Color-coded: Green (Low), Yellow (Medium), Red (High)
Displays harm index with smooth transitions
Risk level badge with gradient backgrounds
Uncertainty indicator (±% display)
EmotionBars.tsx

Horizontal animated bars for 5 emotions:
Anger 😠 (Red)
Fear 😨 (Orange)
Joy 😊 (Green)
Sadness 😢 (Blue)
Neutral 😐 (Gray)
Shimmer animation effects
Emotional intensity warning system
ExplanationPanel.tsx

Expandable accordion sections:
Overview: Summary of assessment
Intent & Call-to-Action: Detects CTAs and dog-whistles
Truth Verification: Similarity to false narratives
Potential Consequences: Historical outcome predictions
Color-coded outcome badges (High/Medium/Low)
Advisory disclaimer messaging
Design System
index.css

CSS variables for consistent theming
Glassmorphism effects with backdrop blur
Dark mode optimized color palette
Animation keyframes (fadeIn, slideIn, shimmer, pulse)
Responsive grid layouts
Custom scrollbar styling
2. Backend API Server (Node.js + Express + TypeScript)
server/src/index.ts

Express server on port 3000
CORS enabled for cross-origin requests
Health check endpoint: GET /health
Main analysis endpoint routing
server/src/routes/analyze.ts

POST /api/analyze endpoint
Orchestrates parallel ML service calls:
Emotion detection → port 8001
Intent classification → port 8002
RAG truth verification → port 8003
Aggregates results into harm assessment
Graceful fallback if ML services unavailable
server/src/services/harmIndex.ts

Weighted formula implementation:
Harm Index = 
  Emotion Volatility × 25 +
  Intent Risk × 30 +
  Historical Harm × 30 +
  Truth Uncertainty × 15
Risk level classification (Low/Medium/High)
Historical outcome generation based on patterns
Explainable narrative generation
Confidence interval calculation
3. Python ML Microservices
emotion_service.py
 (Port 8001)

HuggingFace j-hartmann/emotion-english-distilroberta-base model
7-emotion classification → mapped to 5 categories
FastAPI endpoint: POST /analyze
Returns emotion scores 0-1 for anger, fear, joy, sadness, neutral
GPU support with automatic fallback to CPU
intent_service.py
 (Port 8002)

Uses unitary/toxic-bert for toxicity detection
Custom pattern matching for:
Explicit CTAs: "share urgently", "boycott", "protest"
Implicit CTAs: "you should", "before it's too late"
Dog-whistles: "they are planning", "wake up sheeple"
Intent classification:
Informational
Persuasive
Action-oriented
Alarmist
Inciting
Returns structured intent analysis with probabilities
rag_service.py
 (Port 8003)

ChromaDB vector database for similarity search
Sentence Transformers all-MiniLM-L6-v2 for embeddings
Seeded knowledge corpus with 8 false narratives:
Vaccine misinformation
5G conspiracy theories
COVID-19 myths
Election fraud claims
Social/political misinformation
Returns:
Similarity score to known false narratives
Evidence confidence (High/Medium/Low)
Similar historical claims
Contradictory source indicators


🏗️ Architecture
<img width="649" height="331" alt="image" src="https://github.com/user-attachments/assets/b7d44759-de6a-4058-af7c-7951b0432440" />



HTTP POST /api/analyze
Parallel Requests
Parallel Requests
Parallel Requests
Vector Search
Emotion Scores
Intent Analysis
Truth Verification
Harm Assessment
Render
Render
Render
React Frontend :5173
Node.js API :3000
Emotion Service :8001
Intent Service :8002
RAG Service :8003
ChromaDB
RiskMeter Component
EmotionBars Component
ExplanationPanel Component
🚀 How to Run
Terminal 1: Frontend
npm run dev
Runs on http://localhost:5173

Terminal 2: Backend API
cd server
npm run dev
Runs on http://localhost:3000

Terminal 3: ML Services
cd ml-services
.\start_services.ps1
Starts three services:

Emotion: http://localhost:8001
Intent: http://localhost:8002
RAG: http://localhost:8003
Note: First run downloads ~500MB of ML models. Wait for "✅ Model loaded successfully!" messages.

🧪 Testing
Test Case 1: High-Risk Misinformation
Input:

They are mixing poison in vaccines. Share this urgently before it's too late!
Expected Results:

Harm Index: 70-90 (High Risk)
Emotions: High anger (70%+), High fear (60%+)
Intent: Alarmist or Inciting
CTAs: Explicit CTA detected ("share urgently")
Dog-Whistle: Medium-high probability
Truth: High similarity to debunked vaccine misinformation
Outcomes: Panic behavior, rapid spread
Test Case 2: Neutral Statement
Input:

The weather forecast predicts rain tomorrow.
Expected Results:

Harm Index: 0-20 (Low Risk)
Emotions: High neutral (80%+)
Intent: Informational
CTAs: None detected
Truth: Low similarity to false narratives
Test Case 3: Dog-Whistle Pattern
Input:

They are planning something tonight. Be alert.
Expected Results:

Harm Index: 40-60 (Medium Risk)
Emotions: Moderate fear
Intent: Action-oriented
CTAs: Implicit CTA detected
Dog-Whistle: High probability (coded language)
📊 Features Implemented
✅ Core Functionality
 Text input with real-time analysis
 Multi-dimensional harm assessment
 Emotion detection (5 categories)
 Intent classification (5 types)
 CTA detection (explicit + implicit)
 Dog-whistle pattern recognition
 RAG-based truth verification
 Historical harm prediction
 Weighted harm index formula
 Explainable assessments
✅ UI/UX
 Animated risk meter (0-100)
 Emotion visualization bars
 Expandable explanation panels
 Dark mode glassmorphism design
 Loading states & error handling
 Responsive layout
 Advisory disclaimer messaging
✅ Backend & ML
 Microservices architecture
 Parallel service orchestration
 Graceful fallbacks
 HuggingFace emotion model
 Toxicity-based intent detection
 Vector database (ChromaDB)
 Sentence embeddings
 Knowledge corpus seeding
📁 Project Structure
kruu-grasp/
│
├── src/                          # Frontend
│   ├── components/
│   │   ├── ChatInterface.tsx
│   │   ├── RiskMeter.tsx
│   │   ├── EmotionBars.tsx
│   │   └── ExplanationPanel.tsx
│   ├── services/
│   │   └── api.ts
│   ├── types.ts
│   ├── index.css
│   └── App.tsx
│
├── server/                       # Backend API
│   └── src/
│       ├── index.ts
│       ├── routes/
│       │   └── analyze.ts
│       └── services/
│           └── harmIndex.ts
│
└── ml-services/                  # Python ML
    ├── emotion_service.py
    ├── intent_service.py
    ├── rag_service.py
    ├── requirements.txt
    ├── start_services.ps1
    └── chroma_db/               # Auto-generated vector DB
🎨 UI Highlights
Risk Meter
SVG-based circular progress
Smooth 1-second animation
Color transitions: Green → Yellow → Red
Glow effects using drop-shadow filters
Displays both index (0-100) and uncertainty (±%)
Emotion Bars
Animated width transitions (1s duration)
Shimmer overlay effect
Emoji indicators for each emotion
Percentage display on right
Emotional intensity summary
Explanation Panel
4 collapsible sections with smooth animations
Icon-based navigation
Color-coded outcome badges
Markdown-style formatting
Advisory footer messaging
🔧 Configuration
Environment Variables:

Frontend (
.env
):

VITE_API_URL=http://localhost:3000
Backend (
server/.env
):

PORT=3000
EMOTION_SERVICE_URL=http://localhost:8001
INTENT_SERVICE_URL=http://localhost:8002
RAG_SERVICE_URL=http://localhost:8003
🔮 MVP Limitations & Future Enhancements
Current Limitations
English-only (Indic languages planned)
Limited knowledge corpus (8 seed examples)
No persistent storage
No user accounts
Text-only (no images/videos)
No time-series analysis
Planned Phase 2 Features
Multilingual Support

Hindi, Tamil, Hinglish models
Code-switched text handling
Expanded Knowledge Base

Integration with fact-check APIs (AltNews, BOOM)
Government advisories (WHO, ICMR)
Real-time news verification
Time-Series Analysis

Historical harm pattern learning
Temporal context awareness
Outbreak prediction
Multimodal Analysis

Image OCR + analysis
Video transcription
Deepfake detection
Production Features

User authentication
Analysis history
Exportable reports
API rate limiting
Caching layer
⚠️ Important Notes
This tool provides advisory guidance, not absolute truth

Not intended for automated censorship
Designed to empower users with information
Should be used alongside critical thinking
Always verify from trusted sources
MVP for research and demonstration
🎯 Key Achievements
✅ Research-Grade Problem Formulation
Shifted from binary truth/false to harm-based assessment

✅ Multi-Dimensional Analysis
Emotion + Intent + Truth + Historical Context

✅ Explainable AI
Every risk score has detailed reasoning

✅ Premium UX
Modern, animated, glassmorphism design

✅ Scalable Architecture
Microservices enable independent scaling

✅ Production-Ready Foundation
TypeScript, error handling, graceful degradation

📚 Technical Stack
Layer	Technology
Frontend	React 18, TypeScript, Vite
Styling	Vanilla CSS, CSS Variables
API Server	Node.js, Express, TypeScript
ML Services	Python 3.9+, FastAPI, Uvicorn
Emotion Model	HuggingFace DistilRoBERTa
Intent Model	Toxic-BERT + Regex Patterns
Embeddings	Sentence Transformers (MiniLM)
Vector DB	ChromaDB
Package Manager	npm (frontend/backend), pip (ML)
🔗 Quick Links
Frontend: http://localhost:5173
Backend API: http://localhost:3000/api/analyze
Health Check: http://localhost:3000/health
Emotion Service: http://localhost:8001/docs
Intent Service: http://localhost:8002/docs
RAG Service: http://localhost:8003/docs
