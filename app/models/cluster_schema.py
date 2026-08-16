from typing import List, Optional
from pydantic import BaseModel, Field

# defining the schema for the clustering request payload


class ClusterRequest(BaseModel):
    text: str = Field(...,
                      min_length=1,
                      description="The user's statement or sentence to be clustered",
                      examples=["Spain won FIFA World Cup 2026",
                                "The U.S. administration expanded global import duties by 10% to 12.5 percent across roughly 60 countries",
                                " The White House renewed efforts seeking to remove Federal Reserve Governor Lisa Cook.",
                                "Cristiano Ronaldo and Georgina Rodriguez officially tied the knot after being together for 10 years."
                                ]
                      )

# defining the schema for a single clustered document object


class ClusteredDocument(BaseModel):
    id: str = Field(
        alias="_id", description="The stringified MongoDB ObjectId")
    document: str
    true_category: Optional[str] = None
    cluster: int
    predicted_category: str

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
