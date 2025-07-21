from connection import SessionLocal
from model import Video

class VideoDataProvider:
    def __init__(self):
        self.db = SessionLocal()

    def add_videos_bulk(self, videos_list):
        # videos_list: List of dicts with keys: { video_id, title, description, published_at }
        try:
            videosToInsert = []
            for v in videos_list:
                video = Video(
                    video_id=v["video_id"],
                    title=v["title"],
                    description=v.get("description"),  # use .get() in case it's missing
                    published_at=v["published_at"]
                )
                videosToInsert.append(video)

            if videosToInsert:
                self.db.bulk_save_objects(videosToInsert)
                self.db.commit()

            return len(videosToInsert)
        except Exception as e:
            self.db.rollback()
            print(f"error: Error adding videos: {e}")
            return -1

    def get_videos_paginated(self, offset=0, limit=10):
        try: 
            query = self.db.query(Video)
            query = query.order_by(Video.published_at.desc())
            query = query.offset(offset).limit(limit)
            return query.all()
        except Exception as e:
            print(f"error: Error fetching videos: {e}")
            return []
    
    def get_total_videos_count(self):
        return self.db.query(Video).count()

    def close(self):
        self.db.close()
