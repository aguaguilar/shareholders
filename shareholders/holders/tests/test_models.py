from datetime import datetime

from django.test import TestCase
from django.db.utils import IntegrityError

from ..models import Person, Organization, Share


class TestPerson(TestCase):
    def test_creation(self):
        person = Person.objects.create(
            name="Agustin",
            postal_code="S2300",
            country="Argentina",
            birth_date=datetime.strptime("1994-11-07", "%Y-%m-%d"),
        )

        self.assertEqual(person.name, "Agustin")
        self.assertEqual(person.postal_code, "S2300")
        self.assertEqual(person.country, "Argentina")
        self.assertEqual(person.birth_date.day, 7)
        self.assertEqual(person.birth_date.month, 11)
        self.assertEqual(person.birth_date.year, 1994)


class TestOrganization(TestCase):
    def test_creation(self):
        organization = Organization.objects.create(
            name="Agustin",
            postal_code="S2300",
            country="Argentina",
            orgnr=10,
        )

        self.assertEqual(organization.name, "Agustin")
        self.assertEqual(organization.postal_code, "S2300")
        self.assertEqual(organization.country, "Argentina")
        self.assertEqual(organization.orgnr, 10)


class TestShare(TestCase):
    def setUp(self):
        self.organization = Organization.objects.create(
            name="Agustin",
            postal_code="S2300",
            country="Argentina",
            orgnr=10,
        )
        self.person = Person.objects.create(
            name="Agustin",
            postal_code="S2300",
            country="Argentina",
            birth_date=datetime.strptime("1994-11-07", "%Y-%m-%d"),
        )

    def test_company_and_person_as_owners(self):
        with self.assertRaises(IntegrityError):
            Share.objects.create(
                person_owner=self.person,
                organization_owner=self.organization,
                organization_owned=self.organization,
                amount=10,
                share_class="othershare",
            )
