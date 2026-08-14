# importing standard library modules
import re
import string
import math
from collections import Counter
from datetime import datetime, timezone

# importing nltk modules
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize

# importing database connections
from app.core import raw_pages_publications, term_index, doc_vectors

# downloading required nltk data (silent)
nltk.download("stopwords", quiet=True)
nltk.download("punkt", quiet=True)
nltk.download("punkt_tab", quiet=True)

# preprocessing the text by applying lowercase, strip non-alphanumerics, tokenize, drop stopwords, and stemming


def preprocess(text):
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    tokens = word_tokenize(text)
    stemmer = PorterStemmer()
    tokens = [stemmer.stem(word) for word in tokens if word not in stopwords.words(
        "english") and word not in string.punctuation and len(word) > 2]
    return " ".join(tokens)

# building the TF-IDF weighted document vectors and the inverted index for terms (title, authors, journal name, volume, number of pages, publish date)

def do_indexing_and_saving():
    print(f"\n{'='*20} Indexing initialization {'='*20}\n")

    docs = list(raw_pages_publications.find({}))
    # total number of publications document
    total_docs = len(docs)

    if total_docs == 0:
        print("No documents found to index.")
        return

    doc_tokens = {}
    df = Counter()

    for doc in docs:
        title_tokens = preprocess(doc.get("title", ""))
        authors_tokens = " ".join(
            [preprocess(author.get("name", "")) for author in doc.get("authors", [])])

        # journal name, volum, and number of pages can be null so if they are empty then an empty [] otherwise preprocess them
        journal_name_tokens = preprocess(
            doc.get("journal_name")) if doc.get("journal_name") else []
        journal_volume_tokens = preprocess(
            doc.get("journal_volume")) if doc.get("journal_volume") else []
        number_of_pages_tokens = preprocess(
            doc.get("number_of_pages")) if doc.get("number_of_pages") else []
        publish_date_tokens = preprocess(
            doc.get("publish_date")) if doc.get("publish_date") else []

        all_doc_string = " ".join([
            title_tokens if isinstance(
                title_tokens, str) else " ".join(title_tokens),
            authors_tokens,
            journal_name_tokens if isinstance(
                journal_name_tokens, str) else " ".join(journal_name_tokens),
            journal_volume_tokens if isinstance(
                journal_volume_tokens, str) else " ".join(journal_volume_tokens),
            number_of_pages_tokens if isinstance(
                number_of_pages_tokens, str) else " ".join(number_of_pages_tokens),
            publish_date_tokens if isinstance(
                publish_date_tokens, str) else " ".join(publish_date_tokens)
        ])

        word_list = all_doc_string.split()

        # extracting URL
        doc_url = doc.get("url")
        if doc_url:
            # storing the actual list of words for the document
            doc_tokens[doc_url] = word_list

        # updating the Document Frequency (DF) counter and applying set() to ensure a word is only counted once per document for the IDF formula
        for term in set(word_list):
            df[term] += 1

    # calculating IDF for each word using the populated df counter
    idf = {term: math.log10(total_docs / (1 + freq)) +
           1 for term, freq in df.items()}

    print(
        f"Processed {total_docs} documents. Vocabulary size: {len(idf)} unique terms.")

    # storing IDF in DB
    if idf:
        term_index.delete_many({})  # before inserting, deleting all older IDFs
        print("Deleted older IDF values from 'term_index' collection")

        # inserting the new IDFs
        term_index.insert_many([
            {
                "term": word,
                "idf": idf_value,
            } for word, idf_value in idf.items()
        ])
        print("Inserted IDF values in 'term_index' collection")

    # storing TF-IDF in DB
    doc_vectors.delete_many({})  # deleting older values from DB
    print("Deleted older vecotrs document from 'doc_vectors' collection")

    #  calculating TF-IDF vectors and normalizing them for cosine similarity
    for doc in docs:
        url = doc.get("url")
        if not url:
            continue

        # fetching the clean list of words (tokens) which is previously processed
        tokens = doc_tokens.get(url, [])

        # counting total number of words otherwise, 1 if they are counted as 0
        total_terms = len(tokens) or 1

        # creating frequency dict to count how many times each unique word appeared
        tf = Counter(tokens)

        # calculating the raw TF-IDF weight for each word
        vector = {term: (count / total_terms) * idf.get(term, 0)
                  for term, count in tf.items()}

        # calculating the L2 norm (Euclidean length) of the document's vector
        norm = math.sqrt(sum(w * w for w in vector.values())) or 1.0

        # normalizing the document vector (TF-IDF)
        vector = {t: w / norm for t, w in vector.items()}

        # preparing the document payload for MongoDB
        vector_document = {
            "url": url,
            # keeping the title alongside the vector makes generating search results much faster later
            "title": doc.get("title", ""),
            "vector": vector,
            # generating a timezone-aware UTC datetime for the timestamp
            "indexed_at": datetime.now(timezone.utc)
        }

        # upserting the normalized vector into the doc_vectors collection
        doc_vectors.update_one(
            {"url": url},
            {"$set": vector_document},
            upsert=True
        )

    print(
        f"Successfully calculated and stored {len(docs)} document vectors in the database.")
    print(f"\n{'='*20} Indexing closed {'='*20}\n")
