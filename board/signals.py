from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.loader import render_to_string

from .models import Reply, Post, Subscription


@receiver(post_save, sender=Reply)
def notify_author_on_reply(sender, instance: Reply, created, **kwargs):
    if not created:
        return
    post = instance.post
    if post.author.email:
        subject = f"Новый отклик на ваше объявление: {post.title}"
        html = render_to_string("emails/new_reply.html", {
            "post": post,
            "reply": instance,
            "site": settings.DEFAULT_FROM_EMAIL,
        })
        text = f"Новый отклик на объявление: {post.title}\n\n{instance.text}"
        msg = EmailMultiAlternatives(subject, text, settings.DEFAULT_FROM_EMAIL, [post.author.email])
        msg.attach_alternative(html, "text/html")
        msg.send(fail_silently=True)


@receiver(post_save, sender=Reply)
def notify_when_reply_accepted(sender, instance: Reply, created, **kwargs):
    if created:
        return
    if instance.accepted and instance.author.email:
        subject = f"Ваш отклик был принят: {instance.post.title}"
        html = render_to_string("emails/reply_accepted.html", {
            "post": instance.post,
            "reply": instance,
            "site": settings.DEFAULT_FROM_EMAIL,
        })
        text = f"Ваш отклик принят для объявления: {instance.post.title}"
        msg = EmailMultiAlternatives(subject, text, settings.DEFAULT_FROM_EMAIL, [instance.author.email])
        msg.attach_alternative(html, "text/html")
        msg.send(fail_silently=True)


@receiver(post_save, sender=Post)
def notify_subscribers_on_new_post(sender, instance: Post, created, **kwargs):
    if not created:
        return
    subs = Subscription.objects.filter(category=instance.category).select_related("user")
    recipients = [s.user.email for s in subs if s.user.email]
    if not recipients:
        return
    subject = f"Новая публикация в вашей категории: {instance.title}"
    html = render_to_string("emails/new_post_newsletter.html", {
        "post": instance,
        "excerpt": instance.excerpt(),
        "site": settings.DEFAULT_FROM_EMAIL,
    })
    text = f"{instance.title}\n\n{instance.excerpt()}"
    msg = EmailMultiAlternatives(subject, text, settings.DEFAULT_FROM_EMAIL, recipients)
    msg.attach_alternative(html, "text/html")
    msg.send(fail_silently=True)
