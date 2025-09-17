from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives
from django.core.management.base import BaseCommand
from django.template.loader import render_to_string

from board.models import Newsletter


class Command(BaseCommand):
    help = "Send unsent newsletters"

    def handle(self, *args, **options):
        items = Newsletter.objects.filter(sent=False)
        for n in items:
            recipients = [u.email for u in User.objects.filter(is_active=True).exclude(email='')]
            html = render_to_string("emails/newsletter.html", {"body": n.body, "subject": n.subject})
            msg = EmailMultiAlternatives(n.subject, n.body, settings.DEFAULT_FROM_EMAIL, recipients)
            msg.attach_alternative(html, "text/html")
            msg.send()
            n.sent = True
            n.save()
            self.stdout.write(self.style.SUCCESS(f"Sent newsletter {n.id} to {len(recipients)}"))
