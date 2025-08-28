from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Any
from fastapi.responses import Response
import datetime
# Import the clean DroolsRAGPipeline class
from drools_rag_pipeline import DroolsRAGPipeline

# ---------- Request/Response Models ----------
class GenerateRequest(BaseModel):
    query: str = Field(..., min_length=3, description="Query for Drools rule generation")
    k: int = Field(15, ge=1, le=50, description="Number of chunks to retrieve")

class Chunk(BaseModel):
    content: str
    score: float

class GenerateResponse(BaseModel):
    drools_code: str

# ---------- FastAPI App ----------
app = FastAPI(
    title="Drools RAG API",
    version="1.0.1",
    description="API for generating Drools rules using RAG pipeline"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- Global Pipeline Instance ----------
pipeline: DroolsRAGPipeline = None

@app.on_event("startup")
async def startup_event():
    """Initialize the pipeline on startup"""
    global pipeline
    try:
        print("Initializing Drools RAG Pipeline...")
        pipeline = DroolsRAGPipeline()

        # Load vector database
        pipeline.load_vector_db()
        print("✅ Pipeline initialized and vector database loaded!")

    except Exception as e:
        print(f"❌ Error initializing pipeline: {str(e)}")
        raise RuntimeError(f"Failed to initialize pipeline: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "pipeline_loaded": pipeline is not None,
        "message": "Drools RAG API is running"
    }

@app.post("/generate")
async def generate_drools_file(request: GenerateRequest):
    """
    Generate Drools rules and return as downloadable .drl file
    """
    if pipeline is None:
        raise HTTPException(
            status_code=503,
            detail="Pipeline not initialized. Check server logs."
        )
    
    try:
        # Load form and Java model content
        form_content = DroolsRAGPipeline.load_form()
        java_model_content = DroolsRAGPipeline.load_java_model()
        
        # Call generate_drools with all required parameters
        drools_code, chunks = pipeline.generate_drools(
            query=request.query,
            form_content=form_content,
            java_model_content=java_model_content,
            k=request.k
        )
        clean_code = drools_code.strip()
        timestamp = datetime.datetime.now().strftime("%m_%d_%H_%M")
        filename = f"generated_rule_{timestamp}.drl"
        
        # Return as downloadable file
        return Response(
            content=clean_code,
            media_type="application/octet-stream",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Required file not found: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating Drools code: {str(e)}"
        )

@app.get("/info")
async def get_info():
    """Get information about loaded resources"""
    if pipeline is None:
        raise HTTPException(status_code=503, detail="Pipeline not initialized")

    try:
        form_content = DroolsRAGPipeline.load_form()
        java_model_content = DroolsRAGPipeline.load_java_model()

        return {
            "form_loaded": "Form content not found" not in form_content,
            "form_size": len(form_content),
            "java_model_loaded": "Java model file not found" not in java_model_content,
            "java_model_size": len(java_model_content),
            "faiss_index_loaded": pipeline.index is not None,
            "metadata_loaded": pipeline.metadata is not None,
            "metadata_entries": len(pipeline.metadata) if pipeline.metadata else 0
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8503)
