from django.urls import re_path, path

from . import consumers

websocket_urlpatterns = [
    #w+ meaning any words match them with room name , $ meaning after / whatever is in url it is not part of room name
    # re_path(r"ws/chat/(?P<room_name>\w+)/$", consumers.ChatConsumer.as_asgi()),
    path('ws/<int:id>/', consumers.ChatConsumer.as_asgi()),
     path('ws/notify/', consumers.NotificationConsumer.as_asgi())
]