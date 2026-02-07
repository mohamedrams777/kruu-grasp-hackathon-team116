from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import torch
import torch.nn as nn
from transformers import BertTokenizer, BertModel, AutoTokenizer, AutoModel
import numpy as np
import uvicorn
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="CNN-BERT Harm Detection Service")

# Global variables for models
tokenizer = None
bert_model = None
cnn_model = None
USE_FALLBACK = True

# Define CNN model for pattern detection
class CNNHarmClassifier(nn.Module):
    def __init__(self, embedding_dim=768, num_filters=128, filter_sizes=[2, 3, 4, 5]):
        super(CNNHarmClassifier, self).__init__()
        self.convs = nn.ModuleList([
            nn.Conv1d(in_channels=embedding_dim, out_channels=num_filters, kernel_size=fs)
            for fs in filter_sizes
        ])
        self.fc1 = nn.Linear(len(filter_sizes) * num_filters, 256)
        self.fc2 = nn.Linear(256, 64)
        self.fc3 = nn.Linear(64, 1)
        self.dropout = nn.Dropout(0.3)
        self.sigmoid = nn.Sigmoid()
        self.relu = nn.ReLU()
    
    def forward(self, x):
        # x shape: (batch_size, seq_len, embedding_dim)
        x = x.permute(0, 2, 1)  # (batch_size, embedding_dim, seq_len)
        
        # Apply convolutions with ReLU
        conv_outputs = [torch.relu(conv(x)) for conv in self.convs]
        
        # Max pooling over time
        pooled = [torch.max(conv_out, dim=2)[0] for conv_out in conv_outputs]
        
        # Concatenate all pooled features
        cat = torch.cat(pooled, dim=1)
        
        # Multi-layer perceptron with dropout
        x = self.dropout(cat)
        x = self.relu(self.fc1(x))
        x = self.dropout(x)
        x = self.relu(self.fc2(x))
        x = self.dropout(x)
        output = self.sigmoid(self.fc3(x))
        
        return output

# Initialize models
logger.info("Loading CNN-BERT hybrid model...")
try:
    # Try loading BERT model
    logger.info("Loading BERT tokenizer and model...")
    tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
    bert_model = BertModel.from_pretrained('bert-base-uncased')
    
    # Initialize CNN model
    cnn_model = CNNHarmClassifier()
    cnn_model.eval()
    
    # Set BERT to evaluation mode
    bert_model.eval()
    
    # Disable gradient computation for inference
    for param in bert_model.parameters():
        param.requires_grad = False
    
    logger.info("✅ CNN-BERT model loaded successfully!")
    USE_FALLBACK = False
    
except Exception as e:
    logger.warning(f"⚠️ Error loading CNN-BERT model: {e}")
    logger.info("Running in Fallback Mode (Pattern-based detection)")
    tokenizer = None
    bert_model = None
    cnn_model = None
    USE_FALLBACK = True


class TextInput(BaseModel):
    text: str


class HarmPrediction(BaseModel):
    harm_score: float
    confidence: float
    bert_features: dict
    cnn_patterns: list


def extract_bert_features(text: str):
    """Extract BERT embeddings from text"""
    if USE_FALLBACK or not tokenizer or not bert_model:
        return None
    
    try:
        # Tokenize with proper padding and truncation
        inputs = tokenizer(
            text, 
            return_tensors='pt', 
            truncation=True, 
            max_length=512, 
            padding='max_length'
        )
        
        # Get BERT embeddings
        with torch.no_grad():
            outputs = bert_model(**inputs)
            embeddings = outputs.last_hidden_state  # (1, seq_len, 768)
        
        return embeddings
    except Exception as e:
        logger.error(f"Error extracting BERT features: {e}")
        return None


def detect_harm_patterns(text: str):
    """Detect harmful patterns using comprehensive keyword analysis"""
    text_lower = text.lower()
    
    patterns = {
        'violence': {
            'keywords': ['kill', 'attack', 'destroy', 'burn', 'fight', 'harm', 'hurt', 'revenge', 
                        'murder', 'assault', 'beat', 'strike', 'eliminate', 'annihilate'],
            'weight': 1.5
        },
        'medical_misinfo': {
            'keywords': ['poison', 'vaccine', 'cure', 'treatment', 'deadly', 'toxic', 'dangerous',
                        'medicine', 'drug', 'disease', 'virus', 'bacteria', 'infection'],
            'weight': 1.3
        },
        'conspiracy': {
            'keywords': ['they', 'hiding', 'control', 'plan', 'secret', 'truth', 'cover-up',
                        'agenda', 'manipulation', 'scheme', 'plot', 'conspiracy'],
            'weight': 1.2
        },
        'urgency': {
            'keywords': ['urgent', 'now', 'immediately', 'before', 'late', 'hurry', 'quick',
                        'asap', 'emergency', 'critical', 'act now'],
            'weight': 1.1
        },
        'cta': {
            'keywords': ['share', 'forward', 'spread', 'tell', 'warn', 'alert', 'boycott',
                        'repost', 'circulate', 'distribute', 'pass on'],
            'weight': 1.4
        },
        'fear': {
            'keywords': ['scared', 'fear', 'afraid', 'terror', 'panic', 'worry', 'threat',
                        'danger', 'risk', 'unsafe', 'vulnerable'],
            'weight': 1.2
        },
        'hate_speech': {
            'keywords': ['hate', 'enemy', 'traitor', 'betrayal', 'against us', 'them vs us',
                        'inferior', 'superior', 'pure', 'contaminated'],
            'weight': 1.6
        },
        'misinformation_markers': {
            'keywords': ['fake news', 'mainstream media', 'they don\'t want you to know',
                        'censored', 'banned', 'suppressed', 'hidden truth'],
            'weight': 1.3
        }
    }
    
    detected = []
    for category, config in patterns.items():
        keywords = config['keywords']
        weight = config['weight']
        matches = [kw for kw in keywords if kw in text_lower]
        if matches:
            # Calculate weighted score
            base_score = len(matches) / len(keywords)
            weighted_score = min(base_score * weight, 1.0)
            detected.append({
                'category': category,
                'matches': matches,
                'score': weighted_score
            })
    
    return detected


@app.post("/predict", response_model=HarmPrediction)
async def predict_harm(input_data: TextInput):
    """Predict harm score using CNN-BERT hybrid model"""
    try:
        # Detect patterns first (works in both modes)
        patterns = detect_harm_patterns(input_data.text)
        
        if USE_FALLBACK:
            # Fallback: Use enhanced pattern-based scoring
            harm_score = 0.0
            if patterns:
                # Weighted average of pattern scores
                total_weight = sum(p['score'] for p in patterns)
                harm_score = min(total_weight / max(len(patterns), 1), 1.0)
            
            # Adjust based on text characteristics
            word_count = len(input_data.text.split())
            if word_count > 50:
                harm_score = min(harm_score * 1.15, 1.0)
            
            # Boost score if multiple high-risk patterns detected
            high_risk_patterns = [p for p in patterns if p['score'] > 0.5]
            if len(high_risk_patterns) >= 3:
                harm_score = min(harm_score * 1.2, 1.0)
            
            logger.info(f"Fallback mode: Harm score = {harm_score:.3f}")
            
            return HarmPrediction(
                harm_score=round(harm_score, 3),
                confidence=0.75,
                bert_features={'fallback': True, 'pattern_count': len(patterns)},
                cnn_patterns=patterns
            )
        
        # Full CNN-BERT mode
        logger.info("Running CNN-BERT prediction...")
        
        # Extract BERT features
        bert_embeddings = extract_bert_features(input_data.text)
        
        if bert_embeddings is None:
            logger.warning("BERT feature extraction failed, using fallback")
            # Fall back to pattern-based scoring
            harm_score = 0.0
            if patterns:
                total_weight = sum(p['score'] for p in patterns)
                harm_score = min(total_weight / max(len(patterns), 1), 1.0)
            
            return HarmPrediction(
                harm_score=round(harm_score, 3),
                confidence=0.6,
                bert_features={'fallback': True, 'error': 'BERT extraction failed'},
                cnn_patterns=patterns
            )
        
        # Run CNN model
        with torch.no_grad():
            cnn_output = cnn_model(bert_embeddings)
            cnn_harm_score = cnn_output.item()
        
        logger.info(f"CNN harm score: {cnn_harm_score:.3f}")
        
        # Combine CNN score with pattern detection
        if patterns:
            pattern_score = sum(p['score'] for p in patterns) / len(patterns)
            # Weighted combination: 70% CNN, 30% patterns
            final_score = (cnn_harm_score * 0.7) + (pattern_score * 0.3)
        else:
            final_score = cnn_harm_score
        
        # Ensure score is in [0, 1]
        final_score = max(0.0, min(1.0, final_score))
        
        # Calculate confidence based on model certainty and pattern agreement
        cnn_confidence = abs(cnn_harm_score - 0.5) * 2  # Higher when far from 0.5
        pattern_confidence = 0.8 if patterns else 0.5
        confidence = (cnn_confidence * 0.6) + (pattern_confidence * 0.4)
        
        logger.info(f"Final harm score: {final_score:.3f}, confidence: {confidence:.3f}")
        
        return HarmPrediction(
            harm_score=round(final_score, 3),
            confidence=round(confidence, 3),
            bert_features={
                'embedding_dim': bert_embeddings.shape[-1],
                'sequence_length': bert_embeddings.shape[1],
                'pattern_count': len(patterns),
                'cnn_score': round(cnn_harm_score, 3)
            },
            cnn_patterns=patterns
        )
    
    except Exception as e:
        logger.error(f"Error predicting harm: {e}", exc_info=True)
        # Return safe fallback response
        patterns = detect_harm_patterns(input_data.text)
        harm_score = 0.3 if patterns else 0.1
        
        return HarmPrediction(
            harm_score=harm_score,
            confidence=0.5,
            bert_features={'error': str(e)},
            cnn_patterns=patterns
        )


@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "service": "cnn-bert-harm-detection",
        "mode": "fallback" if USE_FALLBACK else "full"
    }


if __name__ == "__main__":
    print("Starting CNN-BERT Harm Detection Service on port 8004...")
    uvicorn.run(app, host="0.0.0.0", port=8004)
