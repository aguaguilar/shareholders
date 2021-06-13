from datetime import datetime

from django.test import TestCase
from django.db.utils import IntegrityError

from ..models import Person, Organization, Share
from ..read_only import ReadOnlyDB


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
        self.organization_2 = Organization.objects.create(
            name="Beaufort",
            postal_code="S2300",
            country="Norway",
            orgnr=11,
        )
        self.person = Person.objects.create(
            name="Agustin",
            postal_code="S2300",
            country="Argentina",
            birth_date=datetime.strptime("1994-11-07", "%Y-%m-%d"),
        )

    def tearDown(self):
        read_only_db = ReadOnlyDB()
        read_only_db.database.drop_collection(read_only_db.organization_collection)

    def test_company_and_person_as_owners(self):
        with self.assertRaises(IntegrityError):
            Share.objects.create(
                person_owner=self.person,
                organization_owner=self.organization,
                organization_owned=self.organization,
                amount=10,
                share_class="other",
            )

    def test_create_share_and_read_from_ro_db_person(self):
        rodb = ReadOnlyDB()

        Share.objects.create(
            person_owner=self.person,
            organization_owned=self.organization,
            amount=10,
            share_class="A-aksjer",
        )

        rodb_field = rodb.database[rodb.organization_collection].find_one()

        self.assertEqual(rodb_field["name"], "Agustin")
        self.assertEqual(rodb_field["total_shares"], 10)
        self.assertEqual(rodb_field["_id"], 10)
        self.assertEqual(rodb_field["postal_code"], "S2300")
        self.assertEqual(rodb_field["country"], "Argentina")
        self.assertEqual(rodb_field["persons_owner"][0]["postal_code"], "S2300")
        self.assertEqual(rodb_field["persons_owner"][0]["country"], "Argentina")
        self.assertEqual(rodb_field["persons_owner"][0]["amount"], 10)
        self.assertEqual(rodb_field["persons_owner"][0]["share_class"], "A-aksjer")

    def test_organization_amount_owners(self):
        Share.objects.create(
            person_owner=self.person,
            organization_owned=self.organization,
            amount=10,
            share_class="A-aksjer",
        )

        Share.objects.create(
            person_owner=self.person,
            organization_owned=self.organization,
            amount=10,
            share_class="B-aksje",
        )

        Share.objects.create(
            organization_owner=self.organization,
            organization_owned=self.organization,
            amount=10,
            share_class="B-aksje",
        )

        self.assertEqual(self.organization.number_of_owners, 2)

    def test_number_of_holdings(self):
        Share.objects.create(
            organization_owner=self.organization,
            organization_owned=self.organization,
            amount=10,
            share_class="B-aksje",
        )

        Share.objects.create(
            organization_owner=self.organization,
            organization_owned=self.organization_2,
            amount=10,
            share_class="B-aksje",
        )

        self.assertEqual(self.organization.number_of_holdings, 2)

    def test_organization_has_foreign_holding(self):
        Share.objects.create(
            person_owner=self.person,
            organization_owned=self.organization_2,
            amount=10,
            share_class="A-aksjer",
        )

        self.assertEqual(self.organization.has_foreign_owners, True)

    def test_organization_doesnt_have_foreign_holding(self):
        Share.objects.create(
            organization_owner=self.organization_2,
            organization_owned=self.organization,
            amount=10,
            share_class="A-aksjer",
        )

        self.assertEqual(self.organization.has_foreign_owners, False)

    def test_doesnt_have_multiple_share_class(self):
        Share.objects.create(
            person_owner=self.person,
            organization_owned=self.organization,
            amount=10,
            share_class="A-aksjer",
        )
        Share.objects.create(
            organization_owner=self.organization_2,
            organization_owned=self.organization,
            amount=10,
            share_class="A-aksjer",
        )

        self.assertEqual(self.organization.has_multiple_share_class, False)

    def test_has_multiple_share_class(self):
        Share.objects.create(
            person_owner=self.person,
            organization_owned=self.organization,
            amount=10,
            share_class="A-aksjer",
        )
        Share.objects.create(
            organization_owner=self.organization_2,
            organization_owned=self.organization,
            amount=10,
            share_class="B-aksje",
        )

        self.assertEqual(self.organization.has_multiple_share_class, True)
