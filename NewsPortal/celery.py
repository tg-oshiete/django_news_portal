import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'NewsPortal.settings')

app = Celery('NewsPortal')
app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()


app.conf.beat_schedule = {
    'latest_news_every_week_mailing': {
        'task': 'articles.tasks.send_every_week_email',
        'schedule': crontab(hour=8, minute=0, day_of_week='monday'),
    }
}