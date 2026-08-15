from typing import List
from fastapi import APIRouter

# importing our pydantic models for validation and serialization
from app.models import UserInputValidator, RankingResponse, AuthorModel

# importing our search engine and database collections
from app.services.search_engine import search
from app.core import raw_pages_publications, raw_pages_profiles

router = APIRouter()


@router.post("/", response_model=List[RankingResponse])
def search_documents(payload: UserInputValidator):
    # fetching raw results containing the cosine similarity score and document url
    raw_results = search(payload.query)

    # initializing an empty list to store the formatted json responses
    formatted_results = []

    for score, url in raw_results:
        # fetching the full original document from the raw pages collection using the url
        full_doc = raw_pages_publications.find_one({"url": url})

        # falling back to profile collection just in case a profile matched the query
        if not full_doc:
            full_doc = raw_pages_profiles.find_one({"url": url})

            # skipping if the document isn't found entirely
            if not full_doc:
                continue

        # formatting the authors list by mapping it to the authormodel schema
        authors_list = []
        for author in full_doc.get("authors", []):
            authors_list.append(AuthorModel(
                name=author.get("name", ""),
                link=author.get("link")
            ))

        # mapping the raw document fields to the rankingresponse pydantic model
        formatted_results.append(RankingResponse(
            score=round(score, 4),
            title=full_doc.get("title") or full_doc.get("name") or "No Title",
            title_link=full_doc.get("title_link") or full_doc.get("url"),
            authors=authors_list,
            publish_date=full_doc.get("publish_date"),
            journal_name=full_doc.get("journal_name"),
            journal_volume=full_doc.get("journal_volume"),
            number_of_pages=full_doc.get("number_of_pages")
        ))

    print(f"Length of response data: {len(formatted_results)}")

    # returning the fully constructed list of ranked responses
    return formatted_results
