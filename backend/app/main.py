from fastapi import FastAPI, HTTPException, Query
from backend.app.services.arxiv_service import search_arxiv

app = FastAPI(
    title="ResearchSphere API",
    description="Scientific paper discovery using the arXiv API.",
    version="0.1.0",
)


@app.get("/")
def root():
    return {
        "message": "Welcome to ResearchSphere API",
        "status": "running",
    }


@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "service": "ResearchSphere API",
    }
@app.get("/api/search")
def search_papers(
    q: str = Query(..., min_length=1, description="Scientific paper search keyword"),
    limit: int = Query(default=5, ge=1, le=5),
):
    q = q.strip()

    if not q:
        raise HTTPException(
            status_code=400,
            detail="Search query cannot be empty or contain only spaces.",
        )
    try:
        papers = search_arxiv(q, max_results=limit)

        return {
            "query": q,
            "count": len(papers),
            "results": papers,
        }

    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    except Exception:
        raise HTTPException(
            status_code=502,
            detail="Unable to retrieve papers from arXiv. Please try again.",
        )