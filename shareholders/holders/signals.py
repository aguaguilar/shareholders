from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Share


@receiver(post_save, sender=Share)
def save_in_read_only_db(sender, instance, *args, **kwargs):
    """
    After save it into write-only database (a.k.a psql) we have to save it into read-only db as well.
    """
    instance.save_in_ro_db()
