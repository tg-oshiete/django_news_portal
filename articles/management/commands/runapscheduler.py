import logging
from django.conf import settings
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django.core.management.base import BaseCommand
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution
from django.core.mail import send_mail
from django.core.mail import EmailMessage
import datetime
from articles.models import Post, Category
from django.utils import timezone
from datetime import timedelta
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string


logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(),
    ]
)


# наша задача по выводу текста на экран
def weekly_mailing_subscribers():
    for category in Category.objects.all():
        subscribers = category.subscribers.all()
        new_posts = Post.objects.filter(category=category, creation__gte=timezone.now().date() - timedelta(days=7))
        if subscribers.exists() and new_posts.exists():
            subscribers_emails = [subscriber.email for subscriber in subscribers if subscriber.email]
            subject = f'Еженедельная рассылка по категории: {category.name}'
            html_content = render_to_string('email/weekly_mailing_subscribers.html',{
                'new_posts': new_posts
            })
            msg = EmailMultiAlternatives(
                subject = subject,
                body = html_content,
                from_email = settings.EMAIL_HOST_USER,
                to = subscribers_emails,
            )
            msg.attach_alternative(html_content, "text/html")
            msg.send()



# функция, которая будет удалять неактуальные задачи
def delete_old_job_executions(max_age=604_800):
    """This job deletes all apscheduler job executions older than `max_age` from the database."""
    DjangoJobExecution.objects.delete_old_job_executions(max_age)


class Command(BaseCommand):
    help = "Runs apscheduler."

    def handle(self, *args, **options):
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")

        # добавляем работу нашему задачнику
        scheduler.add_job(
            weekly_mailing_subscribers,
            trigger=CronTrigger(day="*/7",),
            # То же, что и интервал, но задача тригера таким образом более понятна django
            id="my_job",  # уникальный айди
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added job 'my_job'.")

        scheduler.add_job(
            delete_old_job_executions,
            trigger=CronTrigger(
                day_of_week="mon", hour="00", minute="00"
            ),
            # Каждую неделю будут удаляться старые задачи, которые либо не удалось выполнить, либо уже выполнять не надо.
            id="delete_old_job_executions",
            max_instances=1,
            replace_existing=True,
        )
        logger.info(
            "Added weekly job: 'delete_old_job_executions'."
        )

        try:
            logger.info("Starting scheduler...")
            scheduler.start()
        except KeyboardInterrupt:
            logger.info("Stopping scheduler...")
            scheduler.shutdown()
            logger.info("Scheduler shut down successfully!")