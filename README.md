## Backend API Documentation: Assignment of Coventry University (Softwarica College) - Vertical Search Engine

This document outlines the REST API endpoints, expected request payloads, and response schemas for the Vertical Search Engine backend.

### Base URL

- **Local Development:** `http://127.0.0.1:8000`
- **Production:** `https://assignment-cu-publications-vse-api.onrender.com`

---

### Data Models (Schemas)

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
