import os
import uuid
import joblib
import json
from pymongo import MongoClient
from app.core import clustered_docs, client, db


# locating the base 'app' directory dynamically
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# pointing to the pkl and documents directories
PKL_DIR = os.path.join(BASE_DIR, "clustering_tasks", "pkl")
DOCS_DIR = os.path.join(BASE_DIR, "clustering_tasks", "documents")

# loading the trained machine learning artifacts into memory
vectorizer = joblib.load(os.path.join(PKL_DIR, "tfidf_vectorizer.pkl"))
lsa_pipeline = joblib.load(os.path.join(PKL_DIR, "lsa_pipeline.pkl"))
kmeans = joblib.load(os.path.join(PKL_DIR, "kmeans_model.pkl"))

cluster_to_category = joblib.load(
    os.path.join(PKL_DIR, "cluster_to_category.pkl"))

# predicting the cluster and category for a given text


def predict_text(text: str):
    text_vec = vectorizer.transform([text])
    text_lsa = lsa_pipeline.transform(text_vec)

    # extracting the integer cluster id
    predicted_cluster = int(kmeans.predict(text_lsa)[0])
    predicted_category = cluster_to_category[predicted_cluster]

    return predicted_cluster, predicted_category

# adding a user query to the database with true_category as null


def cluster_and_store_query(text: str):
    cluster_id, category = predict_text(text)

    new_document = {
        "document": text,
        "true_category": None,
        "cluster": cluster_id,
        "predicted_category": category
    }

    # inserting into mongodb
    clustered_docs.insert_one(new_document)

    print(f"{10*'='} Clustered new user's statement and saved the result into 'clustered_docs' collection... {10*'='}")

    # converting the mongodb objectid to a string
    new_document["_id"] = str(new_document["_id"])

    return new_document

# deleting all older clustered docs from the database


def delete_all_clustered_docs():
    result = clustered_docs.delete_many({})

    print(f"{10*'='} Deleted all clustered docs from 'clustered_docs' collection... {10*'='}")

    return result.deleted_count

# storing trained json docs into the database


def save_json_docs():
    json_path = os.path.join(DOCS_DIR, "all_docs.json")

    # reading the json file
    with open(json_path, "r", encoding="utf-8") as f:
        dict_clustered_docs = json.load(f)


    # inserting all baseline documents into the db
    if dict_clustered_docs:
        clustered_docs.insert_many(dict_clustered_docs)

    print(f"{10*'='} Saved trained docs into 'clustered_docs' collection from JSON data... {10*'='}")

    return len(dict_clustered_docs)

# resetting the database by clearing all records and re-inserting the base data


def reset_user_queries():
    # executing the delete and insert functions sequentially
    deleted_count = delete_all_clustered_docs()
    inserted_count = save_json_docs()

    return deleted_count, inserted_count

# retrieving all documents from the database


def fetch_all_documents():
    # sorting by _id descending (-1) to ensure the most recently inserted data is at the top
    cursor = clustered_docs.find().sort([("_id", -1)])

    docs = []
    for doc in cursor:
        doc["_id"] = str(doc["_id"])
        docs.append(doc)

    print(f"{10*'='} Fetched all clustered docs... {10*'='}")

    return docs

# setting up clustered docs for the first time


def setup_initial_clustered_db():
    # counting documents efficiently instead of fetching all records into memory
    doc_count = clustered_docs.count_documents({})

    if doc_count == 0:
        print(f"{10*'='} Database is empty. Seeding JSON data... {10*'='}")
        save_json_docs()
    else:
        print(f"{10*'='} Database already contains {doc_count} documents. Skipping JSON insertion... {10*'='}")
