from django.db.models.signals import post_save, post_delete
from django.core.mail import mail_managers
from .models import Post, User
from django.dispatch import receiver
from datetime import datetime
from django.core.mail import send_mail
from django.conf import settings


@receiver(post_save, sender=Post)
def test_notification_signal(sender, instance, created, **kwargs):
    if created:
        subject = f'{instance.type_post}  {instance.title}'
    else:
        subject = f'Изменения для: {instance.type_post}  {instance.title}'
    mail_managers(
        subject = subject,
        message = f'{instance.content}\n{instance.creation.strftime("%d.%m.%Y")}'
    )

@receiver(post_delete, sender=Post)
def test_del_notification_signal(sender, instance, **kwargs):
    mail_managers(
        subject = f'Удаление поста : {instance.type_post}  {instance.title}',
        message = f'{instance.content}\n{instance.creation.strftime("%d.%m.%Y")}'
    )

@receiver(post_save, sender=User)
def welcome_email(sender, instance, created, **kwargs):
    if created:
        send_mail(
            subject = 'Приветстсвенное письмо.',
            message = 'На данном сайте вы можете отслеживать различные новости, читать статьи, подписываться на '
                      'рассылки новых новостей и взаимодействовать с другими читателями, авторами. Приятного пользования.',
            from_email = settings.EMAIL_HOST_USER,
            recipient_list = [instance.email]
        )
