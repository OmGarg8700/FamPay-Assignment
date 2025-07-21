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

    if page_no == 1:
        searchKey = Constants['YOUTUBE_DATA'] + str(page_no) + "_" + str(limit)
        cached_data = redis_client.get(searchKey)
        if cached_data:
            cached_data = json.loads(cached_data)
            print(cached_data)
            return {
                "isError": "false",
                "pageNo": page_no,
                "limit": limit,
                "totalCount": total_count,
                "totalPages": total_pages,
                "videos": cached_data,
            }, 200

    offset = (page_no - 1) * limit
    video_objs = dp.get_videos_paginated(offset=offset, limit=limit)

    result = []
    for v in video_objs:
        result.append({
            "video_id": v.video_id,
            "title": v.title,
            "description": v.description,
            "published_at": v.published_at.isoformat(),
        })

    if page_no == 1:
        searchKey = Constants['YOUTUBE_DATA'] + str(page_no) + "_" + str(limit)
        redis_client.set(searchKey, json.dumps(result))

    return {
        "isError": "false",
        "pageNo": page_no,
        "limit": limit,
        "totalCount": total_count,
        "totalPages": total_pages,
        "videos": result,
    }, 200
