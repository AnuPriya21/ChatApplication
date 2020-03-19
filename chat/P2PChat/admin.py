from django.contrib import admin
from P2PChat.models import Message,UserProfile

admin.site.register(UserProfile)
admin.site.register(Message)