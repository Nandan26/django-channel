from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import UserProfileModel, ChatNotification
import json

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import ChatNotification

@receiver(post_save, sender=ChatNotification)
def send_notification(sender, instance, created, **kwargs):
    print('this signal is called')
    # if created:
    channel_layer = get_channel_layer()
    notification_obj = ChatNotification.objects.filter(is_seen=False, user=instance.user).count()
    user_id = str(instance.user.id)
    data = {
        'count':notification_obj
    }

    # call the send_notification method / event off consumers
    async_to_sync(channel_layer.group_send)(
        user_id, {
            'type':'send_notification',
            'value':json.dumps(data)
        }
    )