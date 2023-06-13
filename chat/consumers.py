import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import ChatModel
from django.contrib.auth.models import User

from .models import ChatNotification
from channels.generic.websocket import WebsocketConsumer, AsyncWebsocketConsumer

# here reddis is used to store channel names and all the channels in one particular group

#  (Channels and the channel layer) they are asynchronous that's why async_to_sync is used
# django models are synchrounous 
# here ChatConsumer only uses async-native libraries (Channels and the channel layer) a
# nd in particular it does not access synchronous Django models. Therefore it can be rewritten to be asynchronous without complications.

# class ChatConsumer(WebsocketConsumer):
#     def connect(self):
#         # get the room name from the url
#         self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        
#         # channel group name
#         self.room_group_name = "chat_%s" % self.room_name

#         # Join room group : add current channel to group
#         async_to_sync(self.channel_layer.group_add)(
#             self.room_group_name, self.channel_name
#         )

#         #accept the connection
#         self.accept()

#     def disconnect(self, close_code):
#         # Leave room group
#         async_to_sync(self.channel_layer.group_discard)(
#             self.room_group_name, self.channel_name
#         )

#     #whenever a client hits send button from frontend the recieve event of consumer will be called

#     # Receive message from WebSocket
#     def receive(self, text_data):

#         #extract the message from event
#         text_data_json = json.loads(text_data)
#         message = text_data_json["message"]

#         print(message, "recieve event is called")

#         # Send message to room group
#         async_to_sync(self.channel_layer.group_send)(
#             self.room_group_name, {"type": "chat_message", "message": message}
#         )

#         # async_to_sync(self.channel_layer.group_send)
#         # Sends an event to a group.
#         # An event has a special 'type' key corresponding to the name of the method that should be invoked on consumers that receive the event.

#     # Function to execute
#     def chat_message(self, event):
#         message = event["message"]

#         # send this event
#         self.send(text_data=json.dumps({"message": message}))
# example of async
# class ChatConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
#         self.room_group_name = "chat_%s" % self.room_name

#         # Join room group
#         await self.channel_layer.group_add(self.room_group_name, self.channel_name)

#         await self.accept()

#     async def disconnect(self, close_code):
#         # Leave room group
#         await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

#     # Receive message from WebSocket/client
#     async def receive(self, text_data):
#         text_data_json = json.loads(text_data)
#         message = text_data_json["message"]

#         # Send message to room group
#         await self.channel_layer.group_send(
#             self.room_group_name, {"type": "chat_message", "message": message}
#         )

#     # Receive message from room group/backend 
#     async def chat_message(self, event):
#         message = event["message"]

#         # Send message to WebSocket/client
#         await self.send(text_data=json.dumps({"message": message}))


class ChatConsumer(AsyncWebsocketConsumer):
    
    #when connection request is sent to webspcket
    async def connect(self):

        #get the user id from the scope
        my_id = self.scope['user'].id
        
        #get the other user id from the url
        other_user_id = self.scope['url_route']['kwargs']['id']

        # create room name
        if int(my_id) > int(other_user_id):
            self.room_name = f'{my_id}-{other_user_id}'
        else:
            self.room_name = f'{other_user_id}-{my_id}'

        #create group name
        self.room_group_name = 'chat_%s' % self.room_name
        #add this room to channel
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        #accept the connection
        await self.accept()

    # when you recieve a message from websocket/ client
    async def receive(self, text_data=None, bytes_data=None):
        data = json.loads(text_data)

        message = data['message']
        username = data['username']
        receiver = data['receiver']

        #save this message to show the history later
        await self.save_message(username, self.room_group_name, message, receiver)
        
        # send it to all the channels which are in this group by calling event chat_message
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'username': username,
            }
        )
    
    #this event will be called 
    async def chat_message(self, event):
        message = event['message']
        username = event['username']

        await self.send(text_data=json.dumps({
            'message': message,
            'username': username
        }))

    # remove this channle from group on disconnection
    async def disconnect(self, code):
        self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # store the message on database since database operations are synchronous we need to call asyn_to_sync database
    @database_sync_to_async
    def save_message(self, username, thread_name, message, receiver):
        chat_obj = ChatModel.objects.create(
            sender=username, message=message, thread_name=thread_name)
        other_user_id = self.scope['url_route']['kwargs']['id']
        get_user = User.objects.get(id=other_user_id)
        if receiver == get_user.username:
            ChatNotification.objects.create(chat=chat_obj, user=get_user)

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        my_id = self.scope['user'].id
        self.room_group_name = f'{my_id}'
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()

    async def disconnect(self, code):
        self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    #this event will be called 
    async def send_notification(self, event):

        data = json.loads(event.get('value'))
        count = data['count']
        print(count)
        await self.send(text_data=json.dumps({
            'count':count
        }))
