from celery import Celery
import dataFetch  # ✅ manually import the file

app = Celery(
    'youtube_data_fetcher',
    broker='redis://redis:6379/0',
    backend='redis://redis:6379/0'
)

app.conf.beat_schedule = {
    'fetch-videos-every-10-seconds': {
        'task': 'dataFetch.fetch_and_store_videos',
        'schedule': 10.0,
    },
}
