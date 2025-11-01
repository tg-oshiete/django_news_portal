from celery import shared_task
import time
from .models import Notifications, Post, User
from django.utils import timezone
from datetime import timedelta
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.conf import settings


@shared_task
def send_notification(post_id): # оптимизировать, чтобы создавался только 1 запрос к базе данных
    post = Post.objects.get(id=post_id)
    categories = post.category.all()
    subscribers = set()
    for category in categories:
        subscribers.update(category.subscribers.all())
    if not subscribers:
        return
    notification = Notifications.objects.create(name = 'Новая новость в подписках!', message=f'{post.title[:50]}...')
    notification.users.add(*subscribers)


@shared_task
def send_every_week_email(): # последними новостями будем считать новости за последние 2 дня
    posts = Post.objects.filter(creation__gte=timezone.now() - timedelta(days=2))
    if not posts.exists():
        return
    from_users = [user.email for user in User.objects.all() if user.email]
    if not from_users:
        return
    html_content = render_to_string('tasks/every_week_email.html', {'posts': posts})
    text_content = "Новости за последние 2 дня: \n\n"
    for post in posts:
        text_content += f"""
        Новая новость: {post.title}

        Дата: {post.creation.strftime('%d.%m.%Y')}

        Краткое содержание: {post.content[:50]}...

        Посмотреть полную версию: http://127.0.0.1:8000{post.get_absolute_url()}
        """

    msg = EmailMultiAlternatives(
        subject = "Новости за последние 2 дня.",
        body = text_content,
        from_email = settings.EMAIL_HOST_USER ,
        to=from_users,
    )
    msg.attach_alternative(html_content, "text/html")
    msg.send()
