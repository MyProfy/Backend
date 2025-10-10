# backend/api/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import ChatRoom, Message, User
from django.core.files.base import ContentFile
import base64

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'
        self.user = self.scope['user']  # Provided by AuthMiddlewareStack

        if self.user.is_anonymous:
            await self.close()
            return

        await self.ensure_room_exists()
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        if text_data:
            text_data_json = json.loads(text_data)
            message_type = text_data_json.get('type', 'message')

            if message_type == 'message':
                message = text_data_json['message']
                await self.save_message(self.user.id, message)
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'chat_message',
                        'message': f"{self.user.name}: {message}",
                        'sender_id': self.user.id
                    }
                )
            elif message_type == 'file':
                file_data = text_data_json['file_data']
                file_name = text_data_json['file_name']
                await self.save_file_message(self.user.id, file_data, file_name)
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'file_message',
                        'file_name': file_name,
                        'sender_id': self.user.id
                    }
                )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'message',
            'message': event['message'],
            'sender_id': event['sender_id']
        }))

    async def file_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'file',
            'file_name': event['file_name'],
            'sender_id': event['sender_id']
        }))

    @database_sync_to_async
    def ensure_room_exists(self):
        try:
            ChatRoom.objects.get(name=self.room_name)
        except ChatRoom.DoesNotExist:
            ChatRoom.objects.create(
                name=self.room_name,
                user1=self.user,
                user2=self.user  # Adjust for real user2 later
            )

    @database_sync_to_async
    def save_message(self, sender_id, content):
        sender = User.objects.get(id=sender_id)
        room = ChatRoom.objects.get(name=self.room_name)
        Message.objects.create(room=room, sender=sender, content=content)

    @database_sync_to_async
    def save_file_message(self, sender_id, file_data, file_name):
        sender = User.objects.get(id=sender_id)
        room = ChatRoom.objects.get(name=self.room_name)
        format, filestr = file_data.split(';base64,')
        ext = format.split('/')[-1]
        data = ContentFile(base64.b64decode(filestr), name=f"{file_name}.{ext}")
        Message.objects.create(room=room, sender=sender, file=data)
