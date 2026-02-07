from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from transformers import pipeline
import torch
import re
import uvicorn

app = FastAPI(title="Intent Classification Service")

# Initialize toxicity/intent classifier
print("Loading intent classification model...")
try:
    from transformers import pipeline
    import torch
    # Using toxicity classifier as proxy for intent detection
    toxicity_classifier = pipeline(
        "text-classification",
        model="unitary/toxic-bert",
        device=0 if torch.cuda.is_available() else -1
    )
    print("✅ Intent model loaded successfully!")
    USE_FALLBACK = False
except Exception as e:
    print(f"Error loading model/libraries: {e}")
    print("Running in Fallback Mode (Simulated Intent)")
    toxicity_classifier = None
    USE_FALLBACK = True


class TextInput(BaseModel):
    text: str


class IntentAnalysis(BaseModel):
    type: str  # Informational, Persuasive, Inciting, Alarmist, Action-oriented
    hasExplicitCTA: bool
    hasImplicitCTA: bool
    dogWhistleProbability: float


def detect_call_to_action(text: str):
    """Detect explicit and implicit calls to action"""
    text_lower = text.lower()
    
    # Explicit CTA patterns
    explicit_patterns = [
        r'\bshare\s+(this|now|urgently|immediately)',
        r'\bforward\s+(this|now|urgently)',
        r'\bspread\s+(the\s+word|awareness)',
        r'\bboycott\b',
        r'\bprotest\b',
        r'\btake\s+action',
        r'\bmust\s+(do|act|share|stop)',
        r'\bdo\s+not\s+(take|believe|trust)',
    ]
    
    hasExplicitCTA = any(re.search(pattern, text_lower) for pattern in explicit_patterns)
    
    # Implicit CTA patterns
    implicit_patterns = [
        r'\byou\s+(should|need\s+to|must)',
        r'\beveryone\s+(should|needs\s+to|must)',
        r'\bwe\s+(should|need\s+to|must)',
        r'\bdon\'t\s+let\b',
        r'\bbefore\s+it\'s\s+too\s+late',
        r'\bwake\s+up',
        r'\bthink\s+about',
    ]
    
    hasImplicitCTA = any(re.search(pattern, text_lower) for pattern in implicit_patterns)
    
    return hasExplicitCTA, hasImplicitCTA


def detect_dog_whistle(text: str):
    """Detect potential coded language or dog whistles"""
    text_lower = text.lower()
    
    # Dog whistle indicators
    dog_whistle_patterns = [
        r'\bthey\b.*\bplanning',
        r'\bthey\b.*\bhiding',
        r'\bthey\b.*\bcontrol',
        r'\bthey\s+don\'t\s+want\s+you\s+to\s+know',
        r'\bthe\s+truth\b.*\bhidden',
        r'\bwake\s+up\s+sheeple',
        r'\bdo\s+your\s+own\s+research',
        r'\bmainstream\s+media.*\blying',
    ]
    
    matches = sum(1 for pattern in dog_whistle_patterns if re.search(pattern, text_lower))
    return min(matches / len(dog_whistle_patterns), 1.0)


def classify_intent_type(text: str, toxicity_score: float, has_cta: bool):
    """Classify the intent type based on text features"""
    text_lower = text.lower()
    
    # Check for alarmist language
    alarmist_keywords = ['urgent', 'emergency', 'crisis', 'disaster', 'danger', 'threat', 'warning']
    alarmist_count = sum(1 for kw in alarmist_keywords if kw in text_lower)
    
    # Check for inciting language
    inciting_keywords = ['attack', 'fight', 'destroy', 'burn', 'kill', 'harm', 'revenge']
    inciting_count = sum(1 for kw in inciting_keywords if kw in text_lower)
    
    # Determine intent type
    if inciting_count >= 2 or toxicity_score > 0.8:
        return 'Inciting'
    elif alarmist_count >= 2 or toxicity_score > 0.6:
        return 'Alarmist'
    elif has_cta:
        return 'Action-oriented'
    elif any(word in text_lower for word in ['should', 'must', 'need to', 'convince']):
        return 'Persuasive'
    else:
        return 'Informational'


@app.post("/analyze", response_model=IntentAnalysis)
async def analyze_intent(input_data: TextInput):
    """Analyze intent and call-to-action in text"""
    try:
        # Detect CTAs
        hasExplicitCTA, hasImplicitCTA = detect_call_to_action(input_data.text)
        
        # Detect dog whistles
        dogWhistleProbability = detect_dog_whistle(input_data.text)
        
        # Get toxicity score
        toxicity_score = 0.0
        
        if USE_FALLBACK:
            # Fallback toxicity heuristic
            bad_words = ['toxic', 'hate', 'stupid', 'idiot', 'kill', 'destroy']
            if any(w in input_data.text.lower() for w in bad_words):
                toxicity_score = 0.9
        elif toxicity_classifier:
            result = toxicity_classifier(input_data.text[:512])[0]
            if result['label'] == 'toxic':
                toxicity_score = result['score']
        
        # Classify intent type
        intent_type = classify_intent_type(
            input_data.text,
            toxicity_score,
            hasExplicitCTA or hasImplicitCTA
        )
        
        return IntentAnalysis(
            type=intent_type,
            hasExplicitCTA=hasExplicitCTA,
            hasImplicitCTA=hasImplicitCTA,
            dogWhistleProbability=dogWhistleProbability
        )
    
    except Exception as e:
        print(f"Error analyzing intent: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "intent-classification"}


if __name__ == "__main__":
    print("Starting Intent Classification Service on port 8002...")
    uvicorn.run(app, host="0.0.0.0", port=8002)
