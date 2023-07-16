from rest_framework import serializers

from notification_app.models import Client, Mailing, Message
from .tasks import test_task, schedule_mailing


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = '__all__'

    @staticmethod
    def validate_phone(value):
        if len(str(value)) != 11:
            raise serializers.ValidationError('Пожалуйста, введите номер '
                                              'в формате 7XXXXXXXXXX (X - цифра от 0 до 9)')
        return value


class MailingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mailing
        fields = '__all__'

    def validate(self, attrs):
        if self.context['request'].method != 'PATCH':
            if attrs['start_time'] > attrs['finish_time']:
                raise serializers.ValidationError('"Финиш" должен быть после "старта"')
        return attrs

    @staticmethod
    def validate_client_filter(value):
        if value is not None:
            mobile_operator_code = value.get('mobile_operator_code')
            tag = value.get('tag')
            if mobile_operator_code is None and tag is None:
                raise serializers.ValidationError('Пожалуйста, задайте атрибуты "tag" и/или "mobile_operator_code"')
        else:
            raise serializers.ValidationError('Пожалуйста, задайте атрибуты "tag" и/или "mobile_operator_code"')
        return value

    # def save(self, **kwargs):
    #     test_task.delay(1)
    #     return super().save(**kwargs)

    def create(self, validated_data):
        """
        :param validated_data:
        :return: instance

        Метод заполняет связанную таблицу Message и запускает асинхронную задачу (рассылку) в Celery
        """
        # test_task.delay(1)

        # Создаем новую рассылку по её параметрам
        mailing = super().create(validated_data)

        # Отфильтровываем нужных клиентов для рассылки сообщений
        client_filter = validated_data.get('client_filter')
        mobile_operator_code = client_filter.get('mobile_operator_code')
        tag = client_filter.get('tag')
        if mobile_operator_code is not None and tag is not None:
            clients = Client.objects.filter(mobile_operator_code=mobile_operator_code, tag=tag)
        elif mobile_operator_code is not None and tag is None:
            clients = Client.objects.filter(mobile_operator_code=mobile_operator_code)
        elif mobile_operator_code is None and tag is not None:
            clients = Client.objects.filter(tag=tag)
        else:
            clients = []

        # Заполняем связанную таблицу Message
        messages = [Message(mailing=mailing, client=client, status='PENDING') for client in clients]
        Message.objects.bulk_create(messages)

        # Запускаем асинхронную задачу (рассылку) в Celery
        context = {
            'start_time': mailing.start_time,
            'finish_time': mailing.finish_time,
            'clients': clients,
            'text': mailing.text,
            'mailing_id': mailing.id
        }
        schedule_mailing.delay(**context)

        return mailing
