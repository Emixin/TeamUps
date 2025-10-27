from channels.generic.websocket import AsyncWebsocketConsumer
import json



class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.username = self.scope['url_route']['kwargs']['username']
        self.group_name = f'notifications_{self.username}'

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        print("WS CONNECT", self.scope['url_route']['kwargs'])
        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        await self.send(text_data=json.dumps({"message": f"Received {data}"}))

    async def send_notification(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({"message": message}))
