import os

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Share
from .amqp import Amqp


@receiver(post_save, sender=Share)
def save_in_read_only_db(sender, instance, *args, **kwargs):
    """
    After save it into write-only database (a.k.a psql) we have to save it into read-only db as well.
    """
    if os.getenv("WRITE_READ_ONLY_ASYNC"):
        amqp = Amqp()
        amqp.publish(str(instance.id))
    else:
        instance.save_in_ro_db()
