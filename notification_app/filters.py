import django_filters

from notification_app.models import Mailing


class MailingFilter(django_filters.FilterSet):
    """Фильтры для рассылок"""

    # задаем только НОВЫЕ фильтры для полей, поведение которых нужно переопределить
    start_time = django_filters.DateFromToRangeFilter()
    finish_time = django_filters.DateFromToRangeFilter()
    text = django_filters.CharFilter(lookup_expr='icontains')

    order_by_field = 'o'
    ordering = django_filters.OrderingFilter(fields=(
        ('start_time', 'start_time'),
        ('finish_time', 'finish_time')
    ))

    class Meta:
        model = Mailing
        fields = ['start_time', 'finish_time', 'text']
