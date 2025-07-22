# 🚀 YouTube Data Fetcher – Async, Cached & Fault-Tolerant API with Celery

![YouTube Data Pipeline](https://raw.githubusercontent.com/your-username/your-repo-name/main/assets/youtube_pipeline.png)

## 📌 Overview

This project demonstrates an optimized, fault-tolerant, and scalable system for fetching YouTube videos using the YouTube Data API v3.

Key features include:
- Clear separation of concerns across data providers, services, and Celery workers.
- Caching of page-1 results with Redis to reduce API hits and speed up response time.
- Scheduled background fetching every 10 seconds using Celery + Beat.
- Fault tolerance by tracking the latest `publishedAt` from the DB itself.
- Multiple API key support with rotation strategy using index-based Redis mapping.
- Secure `.env` management using `.env.sample`.

---

## ⚙️ Architecture

- **Flask API**: Serves endpoints for video retrieval and health checks.
- **Celery with Beat**: Periodically fetches new videos from YouTube.
- **Redis**: Used for caching and internal coordination (e.g., API key indexing).
- **MySQL**: Stores all fetched video metadata.

---

## 🔄 What This Project Does

1. **Decoupled Layers**: Flow is separated across:
   - `dataFetch.py`: Celery task to fetch YouTube data.
   - `dataprovider.py`: Interface to DB access and cache.
   - `service.py`: Handles logic to serve paginated API results.
   - `connection.py`: Manages DB and Redis connections.

2. **Scheduled Fetching**:
   - Celery + Beat runs a background job every 10 seconds.
   - Fetches the latest videos since the last `publishedAt` value in the DB.

3. **Caching for Page 1**:
   - Page 1 with `limit=100` is cached every 10s.
   - Any request to page 1 with a smaller limit (e.g., 10, 50) is served from this cache.

4. **Multiple API Keys**:
   - Keys are added to `.env.sample` as a comma-separated list.
   - Redis maintains only an index, which maps to the key list in memory.
   - This allows safe rotation and avoids overuse of a single key.

---

## ✅ Optimizations

### ✅ Fault Tolerance
- `publishedAfter` for the YouTube API is determined from the latest DB timestamp.
- Even if one or more fetch jobs fail, the next will continue from the correct point.

### ✅ Thundering Herd Prevention
- Instead of updating cache on-demand from multiple concurrent requests:
  - Cache is refreshed centrally by Celery every 10 seconds.
  - This ensures all requests to page 1 hit Redis, not the DB or YouTube API.

### ✅ Caching Strategy
- Page 1 results (limit=100) are cached under a Redis key like `youtube_data_page1`.
- Smaller paginations are sliced directly from this cached list.
- API key index is also stored in Redis for round-robin usage.

### ✅ Celery Choice Justification
- A `while True` loop was avoided.
- Celery with Beat gives reliable scheduling, automatic retries, and log tracking.

---

## 🚀 Future Optimizations

- Store `latest_updated_at` in Redis instead of querying DB.
- Add rate limit and exponential backoff handling.

---

## 🧪 How to Run and Test

### ⚒️ Prerequisites

- Docker and Docker Compose installed
- Ports `5001`, `3307`, and `6379` available

---

### 🏗️ Setup and Run

1. Clone the repo:
   ```bash
   git clone https://github.com/your-username/your-repo-name.git
   cd your-repo-name
