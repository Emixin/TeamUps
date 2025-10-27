from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


def push_notification(username, message):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(f'notifications_{username}',
                                            {'type': 'send_notification', 'message': message})
