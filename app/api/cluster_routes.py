from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.cluster_engine import (
    cluster_and_store_query,
    reset_user_queries,
    fetch_all_documents
)

# initializing the router for clustering endpoints
router = APIRouter(prefix="/api/clustering", tags=["Document Clustering"])

# defining the request body schema using pydantic


class ClusterRequest(BaseModel):
    text: str

# handling the clustering of new user sentences


@router.post("/cluster")
async def cluster_text_endpoint(request: ClusterRequest):
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty.")

    try:
        # processing the text and saving to database
        result = cluster_and_store_query(request.text)
        return {
            "status": "success",
            "message": "Text successfully clustered.",
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# handling the full reset of the clustering database


@router.post("/reset_cluster")
async def reset_cluster_endpoint():
    try:
        # deleting all docs and re-inserting the base json dataset
        deleted_count, inserted_count = reset_user_queries()

        return {
            "status": "success",
            "message": f"Successfully deleted {deleted_count} old documents and re-seeded {inserted_count} baseline documents.",
            "deleted_count": deleted_count,
            "inserted_count": inserted_count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# handling the retrieval of all clustered documents


@router.get("/get_docs")
async def get_docs_endpoint():
    try:
        # fetching all documents for the frontend table
        documents = fetch_all_documents()
        return {
            "status": "success",
            "total_documents": len(documents),
            "data": documents
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
