from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings
import uvicorn
from typing import List
import os

app = FastAPI(title="RAG Truth Verification Service")

# Initialize embedding model and ChromaDB
print("Loading embedding model and RAG system...")
try:
    from sentence_transformers import SentenceTransformer
    import chromadb
    from chromadb.config import Settings
    
    embedder = SentenceTransformer('all-MiniLM-L6-v2')
    print("✅ Embedding model loaded successfully!")
    
    # Modern ChromaDB initialization
    chroma_client = chromadb.PersistentClient(path="./chroma_db")
    
    # Get or create collection
    collection = chroma_client.get_or_create_collection(
        name="misinformation_corpus",
        metadata={"description": "Known false narratives and verified claims"}
    )
    
    # Seed with initial data if empty
    if collection.count() == 0:
        print("Seeding initial knowledge corpus...")
        seed_knowledge_base(collection)
        
    print(f"✅ ChromaDB initialized with {collection.count()} documents")
    USE_FALLBACK = False

except Exception as e:
    print(f"Error loading RAG system: {e}")
    print("Running in Fallback Mode (Simulated RAG)")
    embedder = None
    collection = None
    USE_FALLBACK = True


def seed_knowledge_base(collection):
    """Seed the knowledge base with known misinformation patterns"""
    false_narratives = [
        {
            "text": "Vaccines contain microchips to track people",
            "category": "health_misinformation",
            "verified": False,
            "harm_level": "high"
        },
        {
            "text": "5G towers spread coronavirus and cause diseases",
            "category": "health_misinformation",
            "verified": False,
            "harm_level": "high"
        },
        {
            "text": "COVID-19 vaccines alter your DNA permanently",
            "category": "health_misinformation",
            "verified": False,
            "harm_level": "high"
        },
        {
            "text": "Drinking bleach or disinfectant cures COVID-19",
            "category": "health_misinformation",
            "verified": False,
            "harm_level": "critical"
        },
        {
            "text": "Climate change is a hoax invented by scientists for funding",
            "category": "science_misinformation",
            "verified": False,
            "harm_level": "medium"
        },
        {
            "text": "The Earth is flat and governments are hiding this truth",
            "category": "conspiracy",
            "verified": False,
            "harm_level": "low"
        },
        {
            "text": "Certain communities are poisoning food supplies",
            "category": "social_misinformation",
            "verified": False,
            "harm_level": "critical"
        },
        {
            "text": "Election results were manipulated through vote rigging",
            "category": "political_misinformation",
            "verified": False,
            "harm_level": "high"
        },
    ]
    
    if embedder:
        texts = [item["text"] for item in false_narratives]
        embeddings = embedder.encode(texts).tolist()
        
        collection.add(
            embeddings=embeddings,
            documents=texts,
            metadatas=false_narratives,
            ids=[f"false_{i}" for i in range(len(false_narratives))]
        )


class TextInput(BaseModel):
    text: str


class TruthVerification(BaseModel):
    similarityToFalseNarratives: float
    evidenceConfidence: str  # High, Medium, Low
    contradictorySources: bool
    similarClaims: List[str]


@app.post("/analyze", response_model=TruthVerification)
async def verify_truth(input_data: TextInput):
    """Verify truth using RAG and similarity search"""
    try:
        if USE_FALLBACK:
            # Fallback logic
            triggers = ['vaccine', 'chip', '5g', 'flat earth', 'hoax']
            is_suspicious = any(w in input_data.text.lower() for w in triggers)
            
            return TruthVerification(
                similarityToFalseNarratives=0.8 if is_suspicious else 0.1,
                evidenceConfidence="Low" if is_suspicious else "High",
                contradictorySources=is_suspicious,
                similarClaims=["Simulated related claim: Verified sources contradict this."] if is_suspicious else []
            )

        if not embedder or not collection:
            # Fallback to mock data
            return TruthVerification(
                similarityToFalseNarratives=0.2,
                evidenceConfidence="Medium",
                contradictorySources=False,
                similarClaims=[]
            )
        
        # Generate embedding for input text
        query_embedding = embedder.encode([input_data.text])[0].tolist()
        
        # Search for similar claims
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=3
        )
        
        similar_claims = []
        max_similarity = 0.0
        
        if results['documents'] and results['documents'][0]:
            for doc, distance in zip(results['documents'][0], results['distances'][0]):
                similarity = 1 - distance  # Convert distance to similarity
                similar_claims.append(doc)
                max_similarity = max(max_similarity, similarity)
        
        # Determine evidence confidence based on similarity
        if max_similarity > 0.8:
            evidence_confidence = "High"
            contradictory_sources = True
        elif max_similarity > 0.5:
            evidence_confidence = "Medium"
            contradictory_sources = True
        else:
            evidence_confidence = "Low"
            contradictory_sources = False
        
        return TruthVerification(
            similarityToFalseNarratives=max_similarity,
            evidenceConfidence=evidence_confidence,
            contradictorySources=contradictory_sources,
            similarClaims=similar_claims[:2]  # Return top 2
        )
    
    except Exception as e:
        print(f"Error in truth verification: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "service": "rag-truth-verification",
        "corpus_size": collection.count() if collection else 0
    }


if __name__ == "__main__":
    print("Starting RAG Truth Verification Service on port 8003...")
    uvicorn.run(app, host="0.0.0.0", port=8003)
