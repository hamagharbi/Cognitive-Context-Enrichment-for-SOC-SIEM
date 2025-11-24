from fastapi import FastAPI, HTTPException
from .models import SemanticAnalysisRequest, MitreTechniqueResponse
from .knowledge_base import MitreKnowledgeBase
from .retriever import MitreRetriever
from .llm_reasoner import LLMReasoner
import os
from .json_ingest import ingest_mitre_json

app = FastAPI(title="MITRE Reasoner Microservice")

# Global instances
# Persist directory relative to where app is run
kb = MitreKnowledgeBase(persist_directory="./chroma_db")
retriever = None
reasoner = LLMReasoner()

@app.on_event("startup")
async def startup_event():
    global retriever
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    chroma_dir = "./chroma_db"
    mitre_json_path = os.path.join(base_dir, "data", "enterprise-attack.json")

    if not os.path.exists(chroma_dir):
        print("No vector DB found. Ingesting MITRE JSON...")
        ingest_mitre_json(mitre_json_path)
    else:
        print("Vector DB exists. Loading existing Chroma...")

        try:
            kb.load_existing()
        except Exception as e:
            print("Error loading DB, regenerating:", e)
            ingest_mitre_json(mitre_json_path)

    retriever = MitreRetriever(kb)

@app.post("/analyze", response_model=MitreTechniqueResponse)
async def analyze_semantic_data(request: SemanticAnalysisRequest):
    if not retriever:
        raise HTTPException(status_code=500, detail="Retriever not initialized")
        
    # 1. Retrieve Candidates using semantic_summary
    # We use the summary as the query vector for similarity search
    if isinstance(request.semantic_features, dict):
        flattened_features = []
        for key, value in request.semantic_features.items():
            if isinstance(value, list):
                flattened_features.extend(value)
            else:
                flattened_features.append(str(value))
        request.semantic_features = flattened_features
    candidates = retriever.search(request.semantic_summary, k=request.k)
    
    if not candidates:
        return MitreTechniqueResponse(
            attack_technique="None",
            technique_id="None",
            tactic="None",
            kill_chain_phase="None",
            confidence=0.0,
            explanation="No matching techniques found in knowledge base.",
            related_techniques=[]
        )

    # 2. Reason using LLM (Groq)
    response = reasoner.select_best_technique(
        summary=request.semantic_summary,
        features=request.semantic_features,
        intent=request.intent,
        candidates=candidates
    )
    
    return response

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
