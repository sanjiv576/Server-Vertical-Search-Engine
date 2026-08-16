## Backend API Documentation: Assignment of Coventry University (Softwarica College)

This document outlines the REST API endpoints, expected request payloads, and response schemas for the Vertical Search Engine backend and clustering documents.

### Task 1: Vertical Search Engine

### Base URL

- **Local Development:** `http://127.0.0.1:8000`
- **Production:** `https://assignment-cu-publications-vse-api.onrender.com`

---

### Data Models (Schemas) for Task 1

The frontend must adhere to these TypeScript-equivalent interfaces when sending or receiving data.

#### 1. UserInputValidator (Request Payload)

Used to validate incoming search queries.

| Field   | Type     | Constraints       | Description                          |
| :------ | :------- | :---------------- | :----------------------------------- |
| `query` | `string` | Minimum length: 1 | The search term entered by the user. |

#### 2. AuthorModel (Sub-schema)

Represents a single author within a publication or profile.

| Field  | Type               | Constraints         | Description                                 |
| :----- | :----------------- | :------------------ | :------------------------------------------ |
| `name` | `string`           | Required            | The full name of the author.                |
| `link` | `string` \| `null` | Optional / Nullable | The URL to the author's university profile. |

#### 3. RankingResponse (Response Payload)

Represents a single search result ranked by the engine. The API returns an array (`List`) of these objects.

| Field             | Type                 | Constraints         | Description                                        |
| :---------------- | :------------------- | :------------------ | :------------------------------------------------- |
| `score`           | `float`              | Required            | The calculated TF-IDF cosine similarity score.     |
| `title`           | `string`             | Required            | The title of the publication or the profile name.  |
| `title_link`      | `string` \| `null`   | Optional / Nullable | The direct URL to the publication or profile.      |
| `authors`         | `Array<AuthorModel>` | Default: `[]`       | List of authors associated with the output.        |
| `publish_date`    | `string` \| `null`   | Optional / Nullable | The formatted publication date (e.g., "May 2026"). |
| `journal_name`    | `string` \| `null`   | Optional / Nullable | The name of the journal.                           |
| `journal_volume`  | `string` \| `null`   | Optional / Nullable | The volume number of the journal.                  |
| `number_of_pages` | `string` \| `null`   | Optional / Nullable | Page count or range (e.g., "15 p.").               |

---

### API Endpoints

#### 1. System Health Check

Verifies that the FastAPI server is running and responsive.

- **Endpoint:** `/health_status`
- **Method:** `GET`
- **Headers:** None
- **Request Body:** None

**Success Response (200 OK):**

```json
{
  "message": "Server is live..."
}
```

#### 2. Trigger Manual Crawl

Manually initiates the web scraping and NLP indexing process in a background thread.

- **Endpoint:** `/trigger-crawl`
- **Method:** `POST`
- **Headers:** None
- **Request Body:** None

**Success Response (202 Accepted):**

```json
{
  "message": "Crawling and indexing started in the background."
}
```

> Note for Frontend Implementation: Because this runs as a background task, the API responds instantly with a 202 status. The actual crawling will take several minutes to complete on the server.

#### 3. Search Index

Queries the indexed TF-IDF database and returns the top 10 ranked documents using cosine similarity.

- **Endpoint:** `/search/`

- **Method:** `POST`

- **Headers:**

- **Content-Type:** `application/json`

- **Request Body:** `UserInputValidator`

**Request Example:**

```json
{
  "query": "A Cross-Sectional Study of Postgraduate Students' Mental Well-Being"
}
```

**Success Response (200 OK):**
Returns a JSON array of RankingResponse objects, sorted in descending order by score.

```json
[
  {
    "score": 0.7821,
    "title": "A Cross-Sectional Study of Postgraduate Students' Mental Well-Being...",
    "title_link": "[https://pureportal.coventry.ac.uk/en/publications/](https://pureportal.coventry.ac.uk/en/publications/)...",
    "authors": [
      {
        "name": "Bisal, N.",
        "link": null
      },
      {
        "name": "Brookes-Smith, C.",
        "link": "[https://pureportal.coventry.ac.uk/en/persons/celine-brookes-smith/](https://pureportal.coventry.ac.uk/en/persons/celine-brookes-smith/)"
      }
    ],
    "publish_date": "May 2026",
    "journal_name": "In: Health Science Reports.",
    "journal_volume": "9",
    "number_of_pages": "15 p."
  }
]
```

---

### Task 2: Clustering Documents

Synthetic data is used for 3 categories: **_"Economics"_**, **_"Entertainment"_**, **_"Politics"_**. Each category has 150 documents, so in total 450 documents are trained under `K-Means algorithm` for clustering them.

### Data Models (Schemas - Task 2)

#### 1. ClusterRequest (Request Payload)

Used to validate incoming statements or sentences prior to clustering.

| Field  | Type     | Constraints       | Description                                       |
| :----- | :------- | :---------------- | :------------------------------------------------ |
| `text` | `string` | Minimum length: 1 | The user's statement or sentence to be clustered. |

#### 2. ClusteredDocument (Sub-schema)

Represents a single clustered document object stored in the database.

| Field                | Type               | Constraints         | Description                                                             |
| :------------------- | :----------------- | :------------------ | :---------------------------------------------------------------------- |
| `_id`                | `string`           | Required            | The stringified MongoDB ObjectId.                                       |
| `document`           | `string`           | Required            | The text content of the document.                                       |
| `true_category`      | `string` \| `null` | Optional / Nullable | The original dataset category, or null for user queries.                |
| `cluster`            | `int`              | Required            | The integer cluster ID produced by K-Means.                             |
| `predicted_category` | `string`           | Required            | The resolved category label predicted for the cluster.                  |
| `confidence`         | `float` \| `null`  | Optional / Nullable | Classification confidence score between 0.0 and 1.0 (higher is better). |

#### 3. ClusterResponse (Response Payload)

Returned upon successfully clustering a new user document.

| Field     | Type                | Constraints | Description                                     |
| :-------- | :------------------ | :---------- | :---------------------------------------------- |
| `status`  | `string`            | Required    | The status string (e.g., "success").            |
| `message` | `string`            | Required    | A descriptive message regarding the clustering. |
| `data`    | `ClusteredDocument` | Required    | The newly processed document cluster object.    |

#### 4. ResetClusterResponse (Response Payload)

Returned upon successfully resetting the clustering dataset.

| Field            | Type     | Constraints | Description                                        |
| :--------------- | :------- | :---------- | :------------------------------------------------- |
| `status`         | `string` | Required    | The status string.                                 |
| `message`        | `string` | Required    | A descriptive message reflecting the reset status. |
| `deleted_count`  | `int`    | Required    | The total number of documents removed.             |
| `inserted_count` | `int`    | Required    | The total number of base documents re-seeded.      |

#### 5. GetDocsResponse (Response Payload)

Returned when retrieving all available clustered documents.

| Field             | Type                       | Constraints | Description                                            |
| :---------------- | :------------------------- | :---------- | :----------------------------------------------------- |
| `status`          | `string`                   | Required    | The status string.                                     |
| `total_documents` | `int`                      | Required    | Total number of documents retrieved from the database. |
| `data`            | `Array<ClusteredDocument>` | Required    | List of all clustered documents.                       |

#### 6. AccuracyEvaluationResponse (Response Payload)

Returned when evaluating overall clustering accuracy using labeled data.

| Field                 | Type              | Constraints         | Description                                                                |
| :-------------------- | :---------------- | :------------------ | :------------------------------------------------------------------------- |
| `status`              | `string`          | Required            | The status string (e.g., "success").                                       |
| `accuracy`            | `float` \| `null` | Optional / Nullable | Accuracy percentage (0-100) based on labeled documents.                    |
| `correct_predictions` | `int`             | Required            | Number of correct predictions (where true_category == predicted_category). |
| `total_labeled`       | `int`             | Required            | Total number of documents with true_category assigned.                     |
| `average_confidence`  | `float` \| `null` | Optional / Nullable | Average confidence score across all documents in the database.             |
| `accuracy_assessment` | `string`          | Required            | Human-readable assessment of clustering accuracy.                          |

---

### API Endpoints (Task 2: Document Clustering)

#### 1. Cluster Text

Clusters a new user sentence using the pre-trained K-Means models and saves the result into the database.

- **Endpoint:** `/clustering/cluster`
- **Method:** `POST`
- **Headers:** Content-Type: `application/json`
- **Request Body:** `ClusterRequest`

**Request Example:**

```json
{
  "text": "Spain won FIFA World Cup 2026"
}
```

**Success Response (200 OK):**

```json
{
  "status": "success",
  "message": "Text successfully clustered.",
  "data": {
    "_id": "6a8129808bde50d1a134a93f",
    "document": "Spain won FIFA World Cup 2026",
    "true_category": null,
    "cluster": 1,
    "predicted_category": "Entertainment",
    "confidence": 0.8234
  }
}
```

#### 2. Reset Cluster Dataset

Deletes all existing clustered documents and repopulates the database exclusively with the base training dataset from the `all_docs.json` file.

- **Endpoint:** `/clustering/reset_cluster`
- **Method:** `POST`
- **Headers:** `None`
- **Request Body:** `None`

**Request Example:**

**Success Response (200 OK):**

```json
{
  "status": "success",
  "message": "Successfully deleted 451 old documents and re-seeded 450 baseline documents.",
  "deleted_count": 451,
  "inserted_count": 450
}
```

#### 3. Get All Clustered Documents

Fetches all clustered documents from the database. The data is sorted in descending order by `_id`, ensuring the most recently inserted user queries appear at the top of the list.

- **Endpoint:** `/clustering/get_docs`
- **Method:** `GET`
- **Headers:** Content-Type: `None`
- **Request Body:** `None`

**Request Example:**

**Success Response (200 OK):**

```json
{
  "status": "success",
  "total_documents": 450,
  "data": [
    {
      "_id": "6a812a1d8bde50d1a134ab01",
      "document": "Natural gas markets experienced high volatility ahead of the winter season.",
      "true_category": "Economics",
      "cluster": 0,
      "predicted_category": "Economics",
      "confidence": 0.7542
    }
  ]
}
```

#### 4. Evaluate Clustering Accuracy

Evaluates the overall clustering accuracy by comparing predicted categories with true categories for labeled documents. Returns accuracy percentage and average confidence metrics.

- **Endpoint:** `/clustering/clustering_accuracy`
- **Method:** `GET`
- **Headers:** `None`
- **Request Body:** `None`

**Request Example:**

**Success Response (200 OK):**

```json
{
  "status": "success",
  "accuracy": 85.5,
  "correct_predictions": 171,
  "total_labeled": 200,
  "average_confidence": 0.7542,
  "accuracy_assessment": "Good - Reasonable clustering accuracy"
}
```

**Response Notes:**

- `accuracy` is calculated only on documents where `true_category` is set (labeled data)
- `correct_predictions` counts documents where `true_category == predicted_category`
- `average_confidence` is computed across ALL documents in the database
- `accuracy_assessment` ranges from "Very Poor" (< 50%) to "Excellent" (≥ 90%)

---

### Classification Confidence & Accuracy Metrics

#### Confidence Score Interpretation

The `confidence` field (0.0 to 1.0) indicates how certain the classification is based on the K-Means distance to the assigned cluster centroid.

| Confidence Range | Interpretation | Recommendation                 |
| :--------------- | :------------- | :----------------------------- |
| **0.8 - 1.0**    | Very High      | Highly reliable classification |
| **0.6 - 0.8**    | High           | Reliable classification        |
| **0.4 - 0.6**    | Medium         | Reasonable classification      |
| **0.2 - 0.4**    | Low            | Consider manual review         |
| **0.0 - 0.2**    | Very Low       | Flag for manual review         |

#### Accuracy Assessment Levels

The `accuracy_assessment` provides a human-readable interpretation of clustering system performance.

| Accuracy Range | Assessment                                |
| :------------- | :---------------------------------------- |
| **≥ 90%**      | Excellent - Very high clustering accuracy |
| **75% - 90%**  | Good - Reasonable clustering accuracy     |
| **60% - 75%**  | Fair - Acceptable clustering accuracy     |
| **50% - 60%**  | Poor - Below average clustering accuracy  |
| **< 50%**      | Very Poor - Clustering needs improvement  |

#### How to Use These Metrics

1. **Classification Confidence**: Use per-document confidence to:
   - Show confidence indicators in the frontend UI
   - Flag low-confidence predictions for manual review
   - Filter results based on confidence thresholds

2. **Clustering Accuracy**: Use system-level accuracy to:
   - Monitor overall system performance
   - Identify when retraining is needed
   - Track improvements over time
   - Label `true_category` on documents to enable accuracy calculation
