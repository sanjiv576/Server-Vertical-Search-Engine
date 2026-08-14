import math
from collections import Counter

# importing the preprocess function we just built
from app.services.nlp_indexer import preprocess

# importing database collections
from app.core import term_index, doc_vectors

# processing user queries and calculating cosine similarity


def build_query_vector(query):
    # processing the query and splitting the resulting string into a clean list of words
    tokens = preprocess(query).split()

    # counting the frequency of each unique word in the user's search query
    tf = Counter(tokens)

    # counting the total number of words in the query for calculating TF
    total_terms = len(tokens) or 1

    # retrieving only the pre-calculated IDF values for the specific words present in the user's query
    idf_docs = term_index.find({"term": {"$in": list(tf.keys())}})

    # mapping the fetched database documents into a fast dictionary lookup format
    idf_map = {d["term"]: d["idf"] for d in idf_docs}

    # calculating the raw TF-IDF weight for each query term
    # and assigning a weight of 0 (via the 'if term in idf_map' condition) to words that don't exist in our database
    vector = {term: (count / total_terms) *
              idf_map[term] for term, count in tf.items() if term in idf_map}

    # calculating the L2 norm (Euclidean length) of the query's vector using the Pythagorean theorem
    norm = math.sqrt(sum(w * w for w in vector.values())) or 1.0

    # normalizing the query vector by dividing each weight by the L2 norm
    # scaling the vector to a length of exactly 1.0 ensures the cosine similarity math works correctly
    return {t: w / norm for t, w in vector.items()}


def cosine_similarity(vec1, vec2):
    # finding the overlapping words that exist in both the search query and the document
    common_terms = set(vec1.keys()) & set(vec2.keys())

    # calculating the dot product of the two normalized vectors
    # because both vectors are normalized (length of 1), the dot product is mathematically equivalent to the cosine similarity
    return sum(vec1[t] * vec2[t] for t in common_terms)


def search(query, top_k=10):
    # generating the normalized TF-IDF vector for the user's search query
    q_vector = build_query_vector(query)

    # exiting early if the query vector is completely empty
    if not q_vector:
        print("no matching terms found in the index.")
        return []

    # initializing an empty list to store matching documents
    results = []

    # iterating through every single pre-calculated document vector stored in the database
    for doc in doc_vectors.find({}):
        # computing the similarity score between the user's query and the current document
        score = cosine_similarity(q_vector, doc["vector"])

        # filtering out documents that share zero words with the query
        if score > 0:
            # appending just the score and URL
            results.append((score, doc["url"]))

    # sorting the matching documents in descending order
    results.sort(key=lambda x: x[0], reverse=True)

    # returning only the top 'k' number of results
    return results[:top_k]
