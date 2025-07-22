import os
import httpx
import asyncio
import json
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from connection import redis_client, init_db
from dataprovider import VideoDataProvider
from celery import shared_task
from constants import Constants

# Load environment variables
load_dotenv()
init_db()

API_KEYS = eval(os.getenv("YOUTUBE_API_KEYS", ""))
SEARCH_QUERY = os.getenv("SEARCH_QUERY", "football")

REDIS_KEY_INDEX = Constants["REDIS_KEY_INDEX"]
MAX_RESULTS = Constants["MAX_RESULTS"]
YOUTUBE_API_URL = Constants["YOUTUBE_API_URL"]
LATEST_PUBLISHED_AT = Constants["LATEST_PUBLISHED_AT"]


def get_api_key():
    if not redis_client:
        raise Exception("Redis client not initialized.")
    
    key_index = redis_client.get(REDIS_KEY_INDEX)
    if key_index is None:
        key_index = 0
    else:
        key_index = int(key_index)

    # Rotate key index
    redis_client.set(REDIS_KEY_INDEX, (key_index + 1) % len(API_KEYS))
    return API_KEYS[key_index]


from datetime import datetime, timedelta, timezone

def get_max_published_at(dp):
    latest_published_at = (datetime.now(timezone.utc) - timedelta(seconds=10)).strftime("%Y-%m-%dT%H:%M:%SZ")

    try:
        latest_video = dp.get_videos_paginated(offset=0, limit=1)
        if latest_video:
            latest_published_at = latest_video[0].published_at.strftime("%Y-%m-%dT%H:%M:%SZ")
        else:
            print("[INFO] No videos found in DB, returning default time.", (datetime.now(timezone.utc) - timedelta(seconds=10)).strftime("%Y-%m-%dT%H:%M:%SZ"))

        return latest_published_at
    except Exception as e:
        print(f"[ERROR] Error fetching max published_at from DB: {e}")
        raise Exception("Failed to fetch max published_at")



async def fetch_latest_videos(dp):
    params = {
        "part": "snippet",
        "q": SEARCH_QUERY,
        "type": "video",
        "order": "date",
        "maxResults": MAX_RESULTS,
        "publishedAfter": get_max_published_at(dp),
        "key": get_api_key()
    }

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(YOUTUBE_API_URL, params=params)
        print(response.text)
        if response.status_code == 403 and "quotaExceeded" in response.text:
            print("[ERROR] YouTube API quota exceeded. Please check your API keys.")

            key_index = redis_client.get(REDIS_KEY_INDEX)
            if key_index is not None:
                redis_client.set(REDIS_KEY_INDEX, (int(key_index) + 1) % len(API_KEYS))
            else:
                redis_client.set(REDIS_KEY_INDEX, 0)

            return []
        
        response.raise_for_status()
        data = response.json()

    videos = []
    for item in data.get("items", []):
        snippet = item["snippet"]
        videos.append({
            "video_id": item["id"]["videoId"],
            "title": snippet["title"],
            "description": snippet.get("description", ""),
            "published_at": datetime.strptime(snippet["publishedAt"], "%Y-%m-%dT%H:%M:%SZ"),
            "thumbnail_default": snippet["thumbnails"]["default"]["url"],
            "thumbnail_medium": snippet["thumbnails"]["medium"]["url"],
            "thumbnail_high": snippet["thumbnails"]["high"]["url"],
        })
    return videos


# @shared_task(name="dataFetch.fetch_and_store_videos")
def fetch_and_store_videos():
    try:
        dp = VideoDataProvider()
        videos = asyncio.run(fetch_latest_videos(dp))

        if videos:
            dp.add_videos_bulk(videos)

            video_objs = dp.get_videos_paginated(offset=0, limit=100)
            cached_data = []
            for v in video_objs:
                cached_data.append({
                    "video_id": v.video_id,
                    "title": v.title,
                    "description": v.description,
                    "published_at": v.published_at.isoformat(),
                    "thumbnail_default": v.thumbnail_default,
                    "thumbnail_medium": v.thumbnail_medium,
                    "thumbnail_high": v.thumbnail_high,
                })

            # Set cache for full 100
            redis_client.set(Constants["YOUTUBE_DATA"], json.dumps(cached_data))

            print(f"[INFO] Upserted videos and cached the results.")
        else:
            print("[INFO] No new videos found.")

    except Exception as e:
        print(f"[ERROR] Exception occurred: {e}")


fetch_and_store_videos()