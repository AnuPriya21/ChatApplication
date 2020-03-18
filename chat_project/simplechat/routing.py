from django.urls import re_path

from simplechat.consumers import ChatConsumer

websocket_urlpatterns = [
    re_path(r'ws/(?P<room_name>\w+)/$',ChatConsumer),
]