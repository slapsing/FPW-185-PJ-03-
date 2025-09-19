from datetime import timedelta

from celery import shared_task
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail, EmailMessage
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.html import strip_tags

from board.models import Post, NewsletterSubscription

User = get_user_model()


@shared_task
def send_weekly_newsletter():
    users = (
        NewsletterSubscription.objects.filter(
            subscribed=True, user__is_active=True
        ).values_list("user", flat=True))

    last_week = timezone.now() - timedelta(days=7)
    posts = Post.objects.filter(created_at__gte=last_week)

    if not posts.exists():
        return "Нет новых постов для рассылки"

    subject = "Новости MMORPGFAN за неделю"
    html_content = render_to_string("emails/newsletter.html", {"posts": posts})
    plain_text = strip_tags(html_content)

    for user in users:
        send_mail(
            subject,
            plain_text,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            html_message=html_content,
            fail_silently=False,
        )

    return f"Рассылка отправлена {users.count()} пользователям"


@shared_task
def send_test_email():
    subject = "Тестовая рассылка Celery"
    message = "Если ты получил это письмо — значит Celery и SMTP настроены правильно ✅"
    recipient_list = ["myemail@mail.ru"]
    email = EmailMessage(subject, message, settings.DEFAULT_FROM_EMAIL, to=recipient_list)
    email.send(fail_silently=False)
    return f"Письмо отправлено на {recipient_list}"
