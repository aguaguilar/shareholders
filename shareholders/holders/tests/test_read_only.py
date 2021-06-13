from django.test import TestCase

from ..read_only import ReadOnlyDB


class TestReadOnlyDB(TestCase):
    def test_connect_to_read_only_db(self):
        ReadOnlyDB()
