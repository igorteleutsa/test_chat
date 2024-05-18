from django.contrib import admin
from .models import Thread, Message


class ThreadAdmin(admin.ModelAdmin):
    list_display = ('id', 'created', 'updated')


class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'sender', 'text', 'thread', 'created', 'is_read')


admin.site.register(Thread, ThreadAdmin)
admin.site.register(Message, MessageAdmin)
