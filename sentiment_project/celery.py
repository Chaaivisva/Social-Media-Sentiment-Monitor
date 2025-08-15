import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sentiment_project.settings')

app = Celery('sentiment_project')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()


app.conf.beat_schedule = {
    'fetch-data-twice-daily': {
        'task': 'social_analyzer.tasks.fetch_data_task',
        'schedule': crontab(minute='0', hour='0,12'),
    },
}