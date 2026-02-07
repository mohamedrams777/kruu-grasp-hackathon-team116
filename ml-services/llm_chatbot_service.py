from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
import uvicorn
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="LLM Chatbot Explanation Service")

# Global variables
tokenizer = None
model = None
USE_FALLBACK = True

# Initialize LLM
logger.info("Loading LLM for explanations...")
try:
    from transformers import GPT2LMHeadModel, GPT2Tokenizer
    import torch
    
    # Load GPT-2 model (using smaller model for faster loading)
    model_name = "gpt2"  # Using base GPT-2 for better compatibility
    logger.info(f"Loading {model_name} model...")
    
    tokenizer = GPT2Tokenizer.from_pretrained(model_name)
    model = GPT2LMHeadModel.from_pretrained(model_name)
    model.eval()
    
    # Set pad token
    tokenizer.pad_token = tokenizer.eos_token
    
    # Disable gradient computation
    for param in model.parameters():
        param.requires_grad = False
    
    logger.info("✅ LLM model loaded successfully!")
    USE_FALLBACK = False
    
except Exception as e:
    logger.warning(f"⚠️ Error loading LLM: {e}")
    logger.info("Running in Fallback Mode (Template-based explanations)")
    tokenizer = None
    model = None
    USE_FALLBACK = True


class AnalysisInput(BaseModel):
    text: str
    harmIndex: int
    riskLevel: str
    emotionScores: Dict[str, float]
    intentAnalysis: Dict[str, Any]
    truthVerification: Dict[str, Any]
    query: Optional[str] = None


class ChatbotResponse(BaseModel):
    explanation: str
    insights: list
    recommendations: list


def generate_template_explanation(analysis: AnalysisInput) -> str:
    """Generate explanation using templates (fallback)"""
    
    harm_level = analysis.riskLevel.lower()
    harm_index = analysis.harmIndex
    
    # Opening
    if harm_level == "high":
        opening = f"⚠️ **High Risk Alert** (Harm Index: {harm_index}/100)\n\n"
        opening += "This statement shows significant potential for harmful impact. "
    elif harm_level == "medium":
        opening = f"⚡ **Moderate Risk** (Harm Index: {harm_index}/100)\n\n"
        opening += "This statement contains concerning elements that warrant attention. "
    else:
        opening = f"✅ **Low Risk** (Harm Index: {harm_index}/100)\n\n"
        opening += "This statement appears relatively benign with minimal harm indicators. "
    
    # Emotional analysis
    emotions = analysis.emotionScores
    dominant_emotion = max(emotions.items(), key=lambda x: x[1])
    
    emotion_text = f"\n\n**Emotional Profile:**\n"
    if dominant_emotion[1] > 0.5:
        emotion_text += f"The statement is heavily charged with **{dominant_emotion[0]}** ({int(dominant_emotion[1]*100)}%), "
        emotion_text += "which can amplify its psychological impact and spread potential."
    else:
        emotion_text += f"The emotional tone is relatively balanced, with mild **{dominant_emotion[0]}** undertones."
    
    # Intent analysis
    intent = analysis.intentAnalysis
    intent_text = f"\n\n**Intent Classification:**\n"
    intent_text += f"Classified as **{intent.get('type', 'Unknown')}**. "
    
    if intent.get('hasExplicitCTA'):
        intent_text += "Contains explicit calls-to-action urging immediate sharing or response. "
    elif intent.get('hasImplicitCTA'):
        intent_text += "Includes subtle prompts encouraging action or dissemination. "
    
    if intent.get('dogWhistleProbability', 0) > 0.5:
        intent_text += "⚠️ Potential coded language or dog-whistles detected."
    
    # Truth verification
    truth = analysis.truthVerification
    truth_text = f"\n\n**Fact-Check Context:**\n"
    
    similarity = truth.get('similarityToFalseNarratives', 0)
    if similarity > 0.7:
        truth_text += f"Shows **high similarity** ({int(similarity*100)}%) to known false narratives. "
    elif similarity > 0.4:
        truth_text += f"Shows **moderate similarity** ({int(similarity*100)}%) to debunked claims. "
    else:
        truth_text += "No strong matches to known misinformation patterns. "
    
    if truth.get('contradictorySources'):
        truth_text += "Verified sources contradict or do not support this claim."
    
    return opening + emotion_text + intent_text + truth_text


def generate_llm_explanation(analysis: AnalysisInput) -> str:
    """Generate explanation using LLM"""
    if USE_FALLBACK or not model or not tokenizer:
        return generate_template_explanation(analysis)
    
    # Create prompt for LLM
    prompt = f"""Analyze this statement for misinformation risk:

Statement: "{analysis.text[:200]}"

Analysis Results:
- Harm Index: {analysis.harmIndex}/100 ({analysis.riskLevel} Risk)
- Dominant Emotion: {max(analysis.emotionScores.items(), key=lambda x: x[1])[0]}
- Intent: {analysis.intentAnalysis.get('type')}
- Similarity to False Narratives: {int(analysis.truthVerification.get('similarityToFalseNarratives', 0)*100)}%

Provide a clear, professional explanation of why this statement received this risk score:"""
    
    try:
        # Tokenize
        inputs = tokenizer(prompt, return_tensors='pt', truncation=True, max_length=512)
        
        # Generate
        with torch.no_grad():
            outputs = model.generate(
                inputs['input_ids'],
                max_length=inputs['input_ids'].shape[1] + 150,
                num_return_sequences=1,
                temperature=0.7,
                top_p=0.9,
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id
            )
        
        # Decode
        generated = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Extract only the generated part (after prompt)
        explanation = generated[len(prompt):].strip()
        
        # If generation is too short or failed, use template
        if len(explanation) < 50:
            return generate_template_explanation(analysis)
        
        return explanation
    
    except Exception as e:
        print(f"LLM generation error: {e}")
        return generate_template_explanation(analysis)


def generate_insights(analysis: AnalysisInput) -> list:
    """Generate key insights from analysis"""
    insights = []
    
    # Emotion insights
    emotions = analysis.emotionScores
    if emotions.get('anger', 0) > 0.6 or emotions.get('fear', 0) > 0.6:
        insights.append("High emotional intensity detected - increases virality potential")
    
    # Intent insights
    intent = analysis.intentAnalysis
    if intent.get('hasExplicitCTA'):
        insights.append("Contains urgent call-to-action - may drive rapid spread")
    
    if intent.get('dogWhistleProbability', 0) > 0.5:
        insights.append("Coded language detected - may target specific audiences")
    
    # Truth insights
    truth = analysis.truthVerification
    if truth.get('similarityToFalseNarratives', 0) > 0.7:
        insights.append("Strong match to known misinformation patterns")
    
    if truth.get('contradictorySources'):
        insights.append("Contradicted by verified fact-checking sources")
    
    # Risk level insight
    if analysis.riskLevel == "High":
        insights.append("Potential for real-world behavioral impact")
    
    return insights


def generate_recommendations(analysis: AnalysisInput) -> list:
    """Generate actionable recommendations"""
    recommendations = []
    
    if analysis.riskLevel == "High":
        recommendations.append("🔍 Verify with multiple trusted sources before sharing")
        recommendations.append("⚠️ Consider the potential consequences of spreading this claim")
        recommendations.append("💬 Engage critically - ask for evidence and sources")
    elif analysis.riskLevel == "Medium":
        recommendations.append("✓ Cross-check with fact-checking organizations")
        recommendations.append("🤔 Look for original sources and context")
        recommendations.append("⏸️ Pause before sharing - verify first")
    else:
        recommendations.append("✓ Appears relatively safe, but always verify important claims")
        recommendations.append("📚 Stay informed from diverse, credible sources")
    
    return recommendations


@app.post("/explain", response_model=ChatbotResponse)
async def explain_analysis(analysis: AnalysisInput):
    """Generate conversational explanation of analysis results"""
    try:
        # Generate main explanation
        explanation = generate_llm_explanation(analysis)
        
        # If using template, ensure it's the template version
        if USE_FALLBACK:
            explanation = generate_template_explanation(analysis)
        
        # Generate insights and recommendations
        insights = generate_insights(analysis)
        recommendations = generate_recommendations(analysis)
        
        return ChatbotResponse(
            explanation=explanation,
            insights=insights,
            recommendations=recommendations
        )
    
    except Exception as e:
        print(f"Error generating explanation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "service": "llm-chatbot-explanation",
        "mode": "fallback" if USE_FALLBACK else "full"
    }


if __name__ == "__main__":
    print("Starting LLM Chatbot Service on port 8005...")
    uvicorn.run(app, host="0.0.0.0", port=8005)
