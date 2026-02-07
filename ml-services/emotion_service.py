from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from transformers import pipeline
import torch
import uvicorn

app = FastAPI(title="Emotion Detection Service")

# Initialize emotion classification model
print("Loading emotion detection model...")
try:
    from transformers import pipeline
    import torch
    # Using a pretrained emotion classifier
    emotion_classifier = pipeline(
        "text-classification",
        model="j-hartmann/emotion-english-distilroberta-base",
        return_all_scores=True,
        device=0 if torch.cuda.is_available() else -1
    )
    print("✅ Emotion model loaded successfully!")
    USE_FALLBACK = False
except Exception as e:
    print(f"Error loading model/libraries: {e}")
    print("Running in Fallback Mode (Simulated Emotion)")
    emotion_classifier = None
    USE_FALLBACK = True


class TextInput(BaseModel):
    text: str


class EmotionScores(BaseModel):
    anger: float
    fear: float
    joy: float
    sadness: float
    neutral: float


@app.post("/analyze", response_model=EmotionScores)
async def analyze_emotion(input_data: TextInput):
    """Analyze emotional content of text"""
    """Analyze emotional content of text"""
    try:
        if USE_FALLBACK:
            # Simple keyword heuristic for fallback
            text_lower = input_data.text.lower()
            scores = {'anger': 0.1, 'fear': 0.1, 'joy': 0.2, 'sadness': 0.1, 'neutral': 0.5}
            
            if any(w in text_lower for w in ['poision', 'kill', 'hate', 'stupid', 'anger']):
                scores['anger'] = 0.7; scores['neutral'] = 0.1
            if any(w in text_lower for w in ['scared', 'fear', 'deadly', 'warning']):
                scores['fear'] = 0.7; scores['neutral'] = 0.1
            if any(w in text_lower for w in ['happy', 'great', 'good', 'joy']):
                scores['joy'] = 0.7; scores['neutral'] = 0.1
            if any(w in text_lower for w in ['sad', 'cry', 'tragedy']):
                scores['sadness'] = 0.7; scores['neutral'] = 0.1
                
            return EmotionScores(**scores)

        if not emotion_classifier:
             # Fallback to mock data if model not loaded (but USE_FALLBACK=False? shouldn't happen)
            return EmotionScores(
                anger=0.1,
                fear=0.1,
                joy=0.3,
                sadness=0.1,
                neutral=0.4
            )

        # Get predictions
        results = emotion_classifier(input_data.text[:512])[0]
        
        # Map model outputs to our emotion categories
        emotion_map = {
            'anger': 0.0,
            'fear': 0.0,
            'joy': 0.0,
            'sadness': 0.0,
            'neutral': 0.0
        }
        
        for item in results:
            label = item['label'].lower()
            score = item['score']
            
            if label in emotion_map:
                emotion_map[label] = score
            elif label == 'disgust':
                emotion_map['anger'] += score * 0.5
                emotion_map['sadness'] += score * 0.5
            elif label == 'surprise':
                emotion_map['neutral'] += score * 0.5
                emotion_map['joy'] += score * 0.5
        
        # Normalize if needed
        total = sum(emotion_map.values())
        if total > 0:
            for key in emotion_map:
                emotion_map[key] /= total
        
        return EmotionScores(**emotion_map)
    
    except Exception as e:
        print(f"Error analyzing emotion: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "emotion-detection"}


if __name__ == "__main__":
    print("Starting Emotion Detection Service on port 8001...")
    uvicorn.run(app, host="0.0.0.0", port=8001)
