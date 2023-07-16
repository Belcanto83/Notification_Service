from django.contrib import admin
from .models import Client, Mailing, Message


class MessageInline(admin.TabularInline):
    model = Message


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('id', 'mobile_operator_code', 'phone', 'tag', 'time_zone')
    list_filter = ['tag', 'mobile_operator_code', 'time_zone']


@admin.register(Mailing)
class MailingAdmin(admin.ModelAdmin):
    list_display = ('id', 'text', 'client_filter', 'start_time', 'finish_time')
    inlines = [MessageInline]


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'status', 'sent_time', 'client', 'mailing')
    list_filter = ['status', 'client']
