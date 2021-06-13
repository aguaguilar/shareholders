from datetime import datetime

from django.test import TestCase, Client

from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_201_CREATED

from ..models import Organization, Person, Share
from ..read_only import ReadOnlyDB


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


class TestShareOwner(TestCase):
    def tearDown(self):
        read_only_db = ReadOnlyDB()
        read_only_db.database.drop_collection(read_only_db.organization_collection)

    def test_get_share_owners(self):
        organization_owned = Organization.objects.create(
            name="Beaufort",
            postal_code="S2300",
            country="Norway",
            orgnr=1,
        )
        person = Person.objects.create(
            name="Agustin",
            postal_code="S2300",
            country="Argentina",
        )
        organization = Organization.objects.create(
            name="Another one",
            postal_code="S2300",
            country="Norway",
            orgnr=2,
        )

        data = {
            "organization_owner": organization.orgnr,
            "organization_owned": organization_owned.orgnr,
            "share_class": "A-aksjer",
            "amount": 10,
        }
        response = self.client.post('/api/share/', data=data)
        self.assertEqual(response.status_code, HTTP_201_CREATED)

        data = {
            "person_owner": person.id,
            "organization_owned": organization_owned.orgnr,
            "share_class": "A-aksjer",
            "amount": 11,
        }
        response = self.client.post('/api/share/', data=data)
        self.assertEqual(response.status_code, HTTP_201_CREATED)

        response = self.client.get('/api/1/owners')
        self.assertEqual(response.json()["organizations_owner"][0]["name"], "Another one")
        self.assertEqual(response.json()["persons_owner"][0]["name"], "Agustin")

    def test_share_owners_not_found(self):
        response = self.client.get('/api/1/owners')
        self.assertEqual(response.status_code, 404)


class TestShareHolding(TestCase):
    def tearDown(self):
        read_only_db = ReadOnlyDB()
        read_only_db.database.drop_collection(read_only_db.organization_collection)

    def test_get_share_holding(self):
        organization_owned_1 = Organization.objects.create(
            name="Beaufort",
            postal_code="S2300",
            country="Norway",
            orgnr=1,
        )
        organization_owned_2 = Organization.objects.create(
            name="Beaufort 2",
            postal_code="S2300",
            country="Norway",
            orgnr=2,
        )

        organization = Organization.objects.create(
            name="Another one",
            postal_code="S2300",
            country="Norway",
            orgnr=4,
        )

        data = {
            "organization_owner": organization.orgnr,
            "organization_owned": organization_owned_1.orgnr,
            "share_class": "A-aksjer",
            "amount": 10,
        }
        response = self.client.post('/api/share/', data=data)
        self.assertEqual(response.status_code, HTTP_201_CREATED)

        data = {
            "organization_owner": organization.orgnr,
            "organization_owned": organization_owned_2.orgnr,
            "share_class": "A-aksjer",
            "amount": 12,
        }
        response = self.client.post('/api/share/', data=data)
        self.assertEqual(response.status_code, HTTP_201_CREATED)

        response = self.client.get('/api/4/holding')
        self.assertEqual(response.json()[0]["name"], "Beaufort")
        self.assertEqual(response.json()[1]["name"], "Beaufort 2")

    def test_share_holding_not_found(self):
        response = self.client.get('/api/1/holding')
        self.assertEqual(response.status_code, 404)


class TestSummary(TestCase):
    def tearDown(self):
        read_only_db = ReadOnlyDB()
        read_only_db.database.drop_collection(read_only_db.organization_collection)

    def test_get_summary(self):
        organization_1 = Organization.objects.create(
            name="Beaufort",
            postal_code="S2300",
            country="Norway",
            orgnr=1,
        )
        organization_2 = Organization.objects.create(
            name="Beaufort 2",
            postal_code="S2300",
            country="Norway",
            orgnr=2,
        )
        organization_3 = Organization.objects.create(
            name="Beaufort 2",
            postal_code="S2300",
            country="Norway",
            orgnr=3,
        )

        organization_4 = Organization.objects.create(
            name="Another one",
            postal_code="S2300",
            country="Argentina",
            orgnr=4,
        )

        data = {
            "organization_owner": organization_2.orgnr,
            "organization_owned": organization_1.orgnr,
            "share_class": "A-aksjer",
            "amount": 10,
        }
        response = self.client.post('/api/share/', data=data)
        self.assertEqual(response.status_code, HTTP_201_CREATED)

        data = {
            "organization_owner": organization_3.orgnr,
            "organization_owned": organization_1.orgnr,
            "share_class": "A-aksjer",
            "amount": 12,
        }
        response = self.client.post('/api/share/', data=data)
        self.assertEqual(response.status_code, HTTP_201_CREATED)

        data = {
            "organization_owner": organization_4.orgnr,
            "organization_owned": organization_1.orgnr,
            "share_class": "B-aksje",
            "amount": 12,
        }
        response = self.client.post('/api/share/', data=data)
        self.assertEqual(response.status_code, HTTP_201_CREATED)

        response = self.client.get('/api/1/summary')

        self.assertEqual(response.json()["number_of_owners"], 3)
        self.assertEqual(response.json()["number_of_holdings"], 0)
        self.assertEqual(response.json()["has_foreign_owners"], True)
        self.assertEqual(response.json()["has_multiple_share_class"], True)

    def test_summary_not_found(self):
        response = self.client.get('/api/1/summary')
        self.assertEqual(response.status_code, 404)
