import logging

from django.core.management.base import BaseCommand

from holders.amqp import Amqp
from holders.models import Share


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Listen and save into ReadOnly Db new shares'

    def handle(self, *args, **options):
        def callback(ch, method, properties, body):
            logger.info("Receiving a new share {}".format(body))
            try:
                share_id = int(body)
            except (TypeError, ValueError):
                raise

            share = Share.objects.get(pk=share_id)
            share.save_in_ro_db()
            logger.info("Share {} was saved into read only database".format(body))

        amqp = Amqp()
        amqp.start_consuming(callback=callback)
