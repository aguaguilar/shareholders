from datetime import datetime

from django.test import TestCase, Client

from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_201_CREATED

from ..models import Organization, Person, Share


class TestOrganization(TestCase):
    def setUp(self):
        self.client = Client()

    def test_create_organization_bad_payload(self):
        response = self.client.post('/api/organization/', data={})
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)

    def test_create_organization(self):
        self.assertEqual(len(Organization.objects.all()), 0)

        data = {
            "orgnr": 1,
            "name": "my company",
            "country": "norway",
            "postal_code": "S3000W",
        }
        response = self.client.post('/api/organization/', data=data)

        self.assertEqual(response.status_code, HTTP_201_CREATED)
        self.assertEqual(len(Organization.objects.all()), 1)


class TestPerson(TestCase):
    def setUp(self):
        self.client = Client()

    def test_create_person_bad_payload(self):
        response = self.client.post('/api/person/', data={})
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)

    def test_create_person(self):
        self.assertEqual(len(Person.objects.all()), 0)

        data = {
            "name": "my company",
            "country": "norway",
            "postal_code": "S3000W",
            "birth_date": datetime.utcnow().date()
        }
        response = self.client.post('/api/person/', data=data)

        self.assertEqual(response.status_code, HTTP_201_CREATED)
        self.assertEqual(len(Person.objects.all()), 1)


class TestShare(TestCase):
    def setUp(self):
        self.client = Client()
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

    def test_create_share_bad_payload(self):
        response = self.client.post('/api/share/', data={})
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)

    def test_create_share(self):
        self.assertEqual(len(Share.objects.all()), 0)

        data = {
            "organization_owner": self.organization.orgnr,
            "organization_owned": self.organization.orgnr,
            "share_class": "A-aksjer",
            "amount": 10,
        }
        response = self.client.post('/api/share/', data=data)

        self.assertEqual(response.status_code, HTTP_201_CREATED)
        self.assertEqual(len(Share.objects.all()), 1)
