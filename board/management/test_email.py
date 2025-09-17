from django.core.mail import send_mail
from django.http import HttpResponse


def test_email(request):
    send_mail(
        subject="Проверка SMTP Яндекс",
        message="Если ты видишь это письмо — SMTP работает!",
        from_email=None,
        recipient_list=["kimer1209@mail.ru"],
    )
    return HttpResponse("Письмо отправлено!")
