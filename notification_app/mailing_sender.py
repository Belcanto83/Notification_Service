import time
import pytz
import datetime
import requests
import os
from django.core.mail import send_mail
from django.conf import settings

from .models import Message


def test_1(task_id):
    print('Test task is started!')  # старт рассылки сообщений на внешнее API
    time.sleep(30)
    print('Test task is done!')
    return f'Task {task_id} is done!'


def send_message(url, headers, json_data, message):
    try:
        # Потоко-безопасное выполнение задач (чтобы 2 раза не отправить одно и то же сообщение)
        message.status = 'PROCESSING'
        message.save()

        response = requests.post(url, headers=headers, json=json_data, timeout=(3.05, 27))
        print('Response status:', response.status_code)
        print(response.json())
        print('*' * 30)
        if response.status_code == 200:
            # Изменяем статус сообщения на "SENT"
            # message = Message.objects.get(client=client, mailing_id=kwargs['mailing_id'])
            message.status = 'SENT'
            message.sent_time = datetime.datetime.now(tz=pytz.timezone(settings.TIME_ZONE))
            message.save()
        else:
            # Изменяем статус сообщения на "ERROR"
            message.status = 'ERROR'
            message.sent_time = datetime.datetime.now(tz=pytz.timezone(settings.TIME_ZONE))
            message.save()

    except requests.exceptions.Timeout:
        # Изменяем статус сообщения на "ERROR"
        message.status = 'ERROR'
        message.sent_time = datetime.datetime.now(tz=pytz.timezone(settings.TIME_ZONE))
        message.save()
        print('Ошибка: Превышено время ожидания ответа сервера')


def mailing_service(**kwargs):
    base_url = 'https://probe.fbrq.cloud/v1/send'

    # Проверяем дату начала рассылки.
    # Если текущее время больше времени начала и меньше времени окончания рассылки,
    # то инициируем рассылку сообщений на внешнее API
    if kwargs['start_time'] < datetime.datetime.now(tz=pytz.timezone(settings.TIME_ZONE)) < kwargs['finish_time']:
        for client in kwargs['clients']:
            headers = {
                'Authorization': f'Bearer {os.getenv("API_TOKEN")}',
                'Content-Type': 'application/json'
            }
            json_data = {
                'id': client.id,
                'phone': client.phone,
                'text': kwargs['text']
            }
            message = Message.objects.get(client=client, mailing_id=kwargs['mailing_id'])
            url = f'{base_url}/{client.id}'
            send_message(url, headers, json_data, message)


def scheduler_service():
    base_url = 'https://probe.fbrq.cloud/v1/send'

    now_time = datetime.datetime.now(tz=pytz.timezone(settings.TIME_ZONE))
    messages_to_send = Message.objects.select_related('mailing').\
        filter(status__in=['PENDING', 'ERROR'], mailing__start_time__lt=now_time, mailing__finish_time__gt=now_time).\
        order_by('sent_time')

    headers = {
        'Authorization': f'Bearer {os.getenv("API_TOKEN")}',
        'Content-Type': 'application/json'
    }
    # print('Messages:', list(messages_to_send))
    # TODO 01: Можно написать генератор групп сообщений (chunks),
    #  т.к. неотправленных сообщений в базе данных может быть очень много.
    #  Генератор выдаёт группу (chunk) сообщений для отправки:
    #  for chunk in messages_to_send_generator:
    #      for message in chunk:
    for message in messages_to_send:
        json_data = {
            'id': message.client.id,
            'phone': message.client.phone,
            'text': message.mailing.text
        }
        # print(json_data)
        url = f'{base_url}/{message.client.id}'
        send_message(url, headers, json_data, message)
    # TODO 04: Если время рассылки истекло, изменить статус соответствующих сообщений на "EXPIRED"


def send_email_with_statistics():
    send_mail(
        'FYI',
        'Test email',
        os.getenv('SEND_FROM'),
        [os.getenv('SEND_TO')],
    )


# TODO 03: Поместить функции (выше) в класс MailingService
# class MailingService:
#     def __init__(self):
#         pass
