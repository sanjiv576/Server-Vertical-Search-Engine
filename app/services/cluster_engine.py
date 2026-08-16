import os
import uuid
import joblib
import json
import numpy as np
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


def calculate_classification_confidence(text: str):
    """
    Calculate confidence score for text classification using K-Means distance.

    Confidence is based on the distance from the sample to its assigned cluster centroid.
    Closer distance = higher confidence (normalized between 0 and 1).

    Args:
        text: Input text to classify

    Returns:
        float: Confidence score between 0 and 1 (higher is better)
    """
    text_vec = vectorizer.transform([text])
    text_lsa = lsa_pipeline.transform(text_vec)

    # Get cluster assignment and distances to all centroids
    distances = kmeans.transform(text_lsa)[0]
    assigned_cluster = int(kmeans.predict(text_lsa)[0])
    distance_to_assigned = distances[assigned_cluster]

    # Calculate confidence as inverse of normalized distance
    # Normalize distance using the maximum distance
    max_distance = np.max(distances)
    if max_distance == 0:
        confidence = 1.0
    else:
        # Confidence: 1 - (normalized distance) to get higher confidence for closer points
        normalized_distance = distance_to_assigned / max_distance
        confidence = max(0.0, 1.0 - normalized_distance)

    return round(float(confidence), 4)


def predict_text_with_confidence(text: str):
    """
    Predict cluster and category for text and return classification confidence.

    Args:
        text: Input text to classify

    Returns:
        dict: {
            'document': text,
            'cluster': predicted_cluster,
            'predicted_category': predicted_category,
            'confidence': confidence_score (0-1, higher is better)
        }
    """
    text_vec = vectorizer.transform([text])
    text_lsa = lsa_pipeline.transform(text_vec)

    predicted_cluster = int(kmeans.predict(text_lsa)[0])
    predicted_category = cluster_to_category[predicted_cluster]
    confidence = calculate_classification_confidence(text)

    return {
        'document': text,
        'cluster': predicted_cluster,
        'predicted_category': predicted_category,
        'confidence': confidence
    }

# adding a user query to the database with true_category as null and confidence score


def cluster_and_store_query(text: str):
    """
    Cluster and store a query with classification confidence score.

    Args:
        text: Query text to classify

    Returns:
        dict: Document with cluster, category, and confidence score
    """
    cluster_id, category = predict_text(text)
    confidence = calculate_classification_confidence(text)

    new_document = {
        "document": text,
        "true_category": None,
        "cluster": cluster_id,
        "predicted_category": category,
        "confidence": confidence
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


def calculate_clustering_accuracy():
    """
    Calculate accuracy rate of clustering by comparing true_category with predicted_category.
    Only evaluates documents where true_category is not None.

    Returns:
        dict: {
            'accuracy': Accuracy percentage (0-100),
            'correct_predictions': Number of correct predictions,
            'total_labeled': Total documents with true_category assigned,
            'average_confidence': Average confidence across all documents,
            'accuracy_assessment': Human-readable assessment
        }
    """
    # Fetch all documents from database
    cursor = clustered_docs.find({})
    docs = list(cursor)

    if len(docs) == 0:
        return {
            'accuracy': None,
            'correct_predictions': 0,
            'total_labeled': 0,
            'average_confidence': None,
            'accuracy_assessment': 'No documents found in database'
        }

    # Filter documents with true_category assigned (labeled data)
    labeled_docs = [doc for doc in docs if doc.get(
        'true_category') is not None]

    # Calculate average confidence across all documents
    all_confidences = [doc.get('confidence', 0) for doc in docs]
    avg_confidence = round(sum(all_confidences) /
                           len(all_confidences), 4) if all_confidences else None

    if len(labeled_docs) == 0:
        return {
            'accuracy': None,
            'correct_predictions': 0,
            'total_labeled': 0,
            'average_confidence': avg_confidence,
            'accuracy_assessment': 'No labeled documents found (true_category not set)'
        }

    # Count correct predictions
    correct_count = sum(
        1 for doc in labeled_docs
        if doc.get('true_category') == doc.get('predicted_category')
    )

    accuracy = (correct_count / len(labeled_docs)) * 100

    # Provide accuracy assessment
    if accuracy >= 90:
        assessment = "Excellent - Very high clustering accuracy"
    elif accuracy >= 75:
        assessment = "Good - Reasonable clustering accuracy"
    elif accuracy >= 60:
        assessment = "Fair - Acceptable clustering accuracy"
    elif accuracy >= 50:
        assessment = "Poor - Below average clustering accuracy"
    else:
        assessment = "Very Poor - Clustering needs improvement"

    print(f"{10*'='} Calculated clustering accuracy: {accuracy:.2f}% {10*'='}")

    return {
        'accuracy': round(accuracy, 2),
        'correct_predictions': correct_count,
        'total_labeled': len(labeled_docs),
        'average_confidence': avg_confidence,
        'accuracy_assessment': assessment
    }

# setting up clustered docs for the first time


def setup_initial_clustered_db():
    # counting documents efficiently instead of fetching all records into memory
    doc_count = clustered_docs.count_documents({})

    if doc_count == 0:
        print(f"{10*'='} Database is empty. Seeding JSON data... {10*'='}")
        save_json_docs()
    else:
        print(f"{10*'='} Database already contains {doc_count} documents. Skipping JSON insertion... {10*'='}")
