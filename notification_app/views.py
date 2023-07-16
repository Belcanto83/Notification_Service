from django.db.models import Count
from django.shortcuts import redirect
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from notification_app.filters import MailingFilter
from notification_app.models import Client, Mailing, Message
from notification_app.serializers import ClientSerializer, MailingSerializer


def index(request):
    return redirect('api/v1/')


def api_documentation(request):
    return redirect('https://app.swaggerhub.com/apis/FAREGO83_1/notification-service-api/1.0.0#/')


class ClientViewSet(ModelViewSet):
    queryset = Client.objects.order_by('id')
    serializer_class = ClientSerializer
    filterset_fields = ['phone', 'mobile_operator_code']
    search_fields = ['tag', 'time_zone']
    ordering_fields = ['mobile_operator_code', 'tag', 'time_zone']


class MailingViewSet(ModelViewSet):
    queryset = Mailing.objects.order_by('-start_time')
    serializer_class = MailingSerializer
    filterset_class = MailingFilter

    @action(detail=True)
    def detailed_statistics(self, request, pk=None):
        """
        :param request:
        :param pk:
        :return: Response

        Формируем детальную статистику по текущей рассылке с группировкой по статусам сообщений
        """
        mailing = self.get_object()
        statuses = mailing.messages.values('status').annotate(total=Count('status')).order_by()
        data = [status for status in statuses]
        s = 0
        for itm in data:
            s += itm['total']
        serializer = self.get_serializer(mailing)
        data.insert(0, serializer.data)
        data.append({'total_messages': s})
        return Response(data)

    @action(detail=False)
    def statistics(self, request):
        """
        :param request:
        :param pk:
        :return: Response

        Формируем общую статистику по всем рассылкам с группировкой по статусам сообщений
        """
        # messages = Message.\
        #                 objects.\
        #                 select_related('mailing').\
        #                 annotate(mail='mailing').\
        #                 order_by('mail').\
        #                 values('mail').\
        #                 annotate(total=Count('id'),
        #                           Sent=Count('id', filter=Q(status='SENT')),
        #                           Pending=Count('id', filter=Q(status='PENDING')),
        #                           Expired=Count('id', filter=Q(status='EXPIRED')),
        #                           Error=Count('id', filter=Q(status='ERROR')),
        #                           Processing=Count('id', status=Q(status='PROCESSING')))

        mailings = Mailing.objects.order_by('-start_time')
        mailings_filtered = self.filter_queryset(mailings)
        page = self.paginate_queryset(mailings_filtered)
        if page is not None:
            res = []
            # TODO 02: уменьшить кол-во запросов к базе (см. QuerySet выше - требуется доработать)
            for mailing in page:
                statuses = mailing.messages.values('status').annotate(total=Count('status')).order_by()
                data = [status for status in statuses]
                s = 0
                for itm in data:
                    s += itm['total']
                serializer = self.get_serializer(mailing)
                data.insert(0, serializer.data)
                data.append({'total_messages': s})
                res.append(data)
            return self.get_paginated_response(res)
        return Response({'status': 0, 'message': 'по вашему запросу ничего не найдено'})
