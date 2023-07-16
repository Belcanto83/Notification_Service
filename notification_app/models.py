from django.db import models


class Mailing(models.Model):
    start_time = models.DateTimeField()
    text = models.TextField()
    client_filter = models.JSONField()
    finish_time = models.DateTimeField()
    # messages


class Client(models.Model):
    phone = models.PositiveBigIntegerField()
    mobile_operator_code = models.PositiveSmallIntegerField()
    tag = models.CharField(max_length=100)
    time_zone = models.CharField(max_length=50)
    # messages


class Message(models.Model):
    class StatusChoices(models.TextChoices):
        SENT = 'SENT', 'Отправлено'
        PENDING = 'PENDING', 'Ожидание отправки'
        EXPIRED = 'EXPIRED', 'Время отправки истекло'
        ERROR = 'ERROR', 'Ошибка отправки'
        PROCESSING = 'PROCESSING', 'В работе (отправка)'

    sent_time = models.DateTimeField(auto_now_add=True)  # auto_now_add=True (если это время СОЗДАНИЯ сообщения!)
    status = models.CharField(max_length=30,
                              choices=StatusChoices.choices,
                              default=StatusChoices.PENDING)
    mailing = models.ForeignKey(Mailing,
                                on_delete=models.CASCADE,
                                related_name='messages')
    client = models.ForeignKey(Client,
                               on_delete=models.CASCADE,
                               related_name='messages')
