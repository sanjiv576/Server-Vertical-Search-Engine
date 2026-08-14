from pymongo import MongoClient
from app.core.config import settings

# initializing MongoDB Client
client = MongoClient(settings.CLOUD_MONGODB_URL)
db = client[settings.CLOUD_DB_NAME]

# defining Collections

# for raw pages of publications (research output)
raw_pages_publications = db["raw_pages_publications"]
# for raw pages of profiles
raw_pages_profiles = db["raw_pages_profiles"]
# for vectors of each document
doc_vectors = db["doc_vectors"]
# for storing IDF
term_index = db["term_index"]
# for storing crawled logs
crawl_log = db["crawl_log"]


def init_db_indexes():
    """
    Creates unique indexes for the database collections to prevent duplicate entries.
    """
    # for storing raw pages of publications and profiles
    raw_pages_publications.create_index("url", unique=True)
    raw_pages_profiles.create_index("url", unique=True)
    # for storing normalized TF-IDF vector per document
    doc_vectors.create_index("url", unique=True)
    # for storing IDF value per word (title, authors, journal name, volume, number of pages, publish date)
    term_index.create_index("term", unique=True)

    print(
        f"Connected to DB: {db.name} | Collections: {db.list_collection_names()}")


init_db_indexes()
