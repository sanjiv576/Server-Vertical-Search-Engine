from typing import List, Optional
from pydantic import BaseModel, Field

# defining the schema for the clustering request payload


class ClusterRequest(BaseModel):
    text: str = Field(...,
                      min_length=1,
                      description="The user's statement or sentence to be clustered",
                      examples=[
                                "Trump says US to reduce military drills with South Korea after it stayed out of Iran war.",
                                "Movie that went viral for terrible animation becomes China box office hit.",
                                "International diplomatic updates highlight ongoing discussions regarding trade, regional policies, and security.",
                                "Taylor Swift and Madonna lead the nominations list for the upcoming MTV Video Music Awards."
                      ])

# defining the schema for a single clustered document object


class ClusteredDocument(BaseModel):
    id: str = Field(
        alias="_id", description="The stringified MongoDB ObjectId")
    document: str
    true_category: Optional[str] = None
    cluster: int
    predicted_category: str
    confidence: Optional[float] = None

# defining the schema for the /cluster endpoint response


class ClusterResponse(BaseModel):
    status: str
    message: str
    data: ClusteredDocument

# defining the schema for the /reset_cluster endpoint response


class ResetClusterResponse(BaseModel):
    status: str
    message: str
    deleted_count: int
    inserted_count: int

# defining the schema for the /get_docs endpoint response


class GetDocsResponse(BaseModel):
    status: str
    total_documents: int
    data: List[ClusteredDocument]

# defining the schema for clustering accuracy evaluation response


class AccuracyEvaluationResponse(BaseModel):
    status: str
    accuracy: Optional[float] = None
    correct_predictions: int
    total_labeled: int
    average_confidence: Optional[float] = None
    accuracy_assessment: str
