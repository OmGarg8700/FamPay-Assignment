import math
import json
from connection import redis_client
from dataprovider import VideoDataProvider
from constants import Constants

dp = VideoDataProvider()

def get_videos_paginated(page_no: int, limit: int):
    if limit not in Constants['LIMIT_VALUES']:
        return {
            "isError": "true",
            "message": f"Invalid limit value. Allowed values are: {Constants['LIMIT_VALUES']}",
        }, 400

    total_count = dp.get_total_videos_count()
    total_pages = math.ceil(total_count / limit) if limit else 1

    if page_no > total_pages and total_pages != 0:
        return {
            "isError": "true",
            "message": "Page number exceeds total pages",
        }, 400

    # FOR PAGE 1 ------------------------
    if page_no == 1:
        cache_key = Constants['YOUTUBE_DATA']
        cached_data = redis_client.get(cache_key)

        if cached_data:
            cached_data = json.loads(cached_data)
            print("[INFO] Returning cached data from Redis for limit=100, slicing for limit:", limit)
            result = cached_data[:limit]  # Slice based on requested limit
        else:
            print("[INFO] Cache not found for page=1. Fetching from DB with limit=100")
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
            redis_client.set(cache_key, json.dumps(cached_data))
            result = cached_data[:limit]  # Slice before returning

        return {
            "isError": "false",
            "pageNo": page_no,
            "limit": limit,
            "totalCount": total_count,
            "totalPages": total_pages,
            "videos": result,
        }, 200

    # DB QUERY FOR OTHER PAGES ------------------------
    offset = (page_no - 1) * limit
    video_objs = dp.get_videos_paginated(offset=offset, limit=limit)

    result = []
    for v in video_objs:
        result.append({
            "video_id": v.video_id,
            "title": v.title,
            "description": v.description,
            "published_at": v.published_at.isoformat(),
            "thumbnail_default": v.thumbnail_default,
            "thumbnail_medium": v.thumbnail_medium,
            "thumbnail_high": v.thumbnail_high,
        })

    return {
        "isError": "false",
        "pageNo": page_no,
        "limit": limit,
        "totalCount": total_count,
        "totalPages": total_pages,
        "videos": result,
    }, 200
