from connection import SessionLocal
from model import Video
from sqlalchemy.dialects.mysql import insert

class VideoDataProvider:
    def __init__(self):
        self.db = SessionLocal()

    def add_videos_bulk(self, videos_list):
        try:
            if not videos_list:
                return 0

            table = Video.__table__

            # Prepare insert statement with upsert logic
            stmt = insert(table).values(videos_list)
            upsert_stmt = stmt.on_duplicate_key_update(
                title=stmt.inserted.title,
                description=stmt.inserted.description,
                published_at=stmt.inserted.published_at
            )

            self.db.execute(upsert_stmt)
            self.db.commit()

            return 1
        except Exception as e:
            self.db.rollback()
            print(f"[ERROR] Error adding videos: {e}")
            return -1

    def get_videos_paginated(self, offset=0, limit=10):
        try: 
            query = self.db.query(Video)
            query = query.order_by(Video.published_at.desc())
            query = query.offset(offset).limit(limit)
            return query.all()
        except Exception as e:
            print(f"[ERROR] Error fetching videos: {e}")
            return []
    
    def get_total_videos_count(self):
        return self.db.query(Video).count()

    def close(self):
        self.db.close()
