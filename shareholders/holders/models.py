from django.db import models
from django.db.models import Q, Count

from .read_only import ReadOnlyDB
from .utils import prepare_data_for_read_only_db


class Person(models.Model):
    name = models.CharField(max_length=255, null=False, blank=False)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=255)
    birth_date = models.DateField(null=True, blank=True)

    def __str__(self) -> str:
        return self.name


class Organization(models.Model):
    name = models.CharField(max_length=255, null=False, blank=False)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=255)
    orgnr = models.IntegerField(primary_key=True)

    def __str__(self) -> str:
        return self.name

    @property
    def total_shares(self) -> int:
        """
        Total shares that the organization has
        """
        return sum([x.amount for x in Share.objects.filter(organization_owned=self).all()])

    @property
    def number_of_owners(self) -> int:
        """
        Amount of share that the organization sold
        """
        return len(
            Share.objects.filter(
                organization_owned=self, organization_owner__isnull=False
            ).values("organization_owner").distinct()
        ) + len(
            Share.objects.filter(organization_owned=self, person_owner__isnull=False).values("person_owner").distinct()
        )

    @property
    def number_of_holdings(self) -> int:
        """
        Amount of shares that the organization bought
        """
        return len(Share.objects.filter(organization_owner=self).values("organization_owned").distinct())

    @property
    def has_foreign_owners(self) -> bool:
        """
        If the organization has foreign owners
        """
        organizations = Share.objects.filter(
            ~Q(organization_owner__country='Norway') & Q(organization_owner__isnull=False)
        )
        persons = Share.objects.filter(
            ~Q(person_owner__country='Norway') & Q(person_owner__isnull=False)
        )

        return True if organizations or persons else False

    @property
    def has_multiple_share_class(self) -> bool:
        """
        If the holders bought different kinds of shares
        """
        return len(
            Share.objects.values('share_class').annotate(dcount=Count('id')).filter(organization_owned=self)
        ) > 1


class Share(models.Model):
    SHARE_CLASS_CHOICES = [
        ("A-aksjer", "A-aksjer"),
        ("B-aksje", "B-aksje"),
    ]

    organization_owner = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="organization_owned_shares",
        null=True,
    )
    person_owner = models.ForeignKey(
        Person,
        on_delete=models.CASCADE,
        related_name="person_owned_shares",
        null=True,
    )
    organization_owned = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="owner_shares"
    )
    share_class = models.CharField(choices=SHARE_CLASS_CHOICES, max_length=8)
    amount = models.IntegerField(default=0)

    def __str__(self) -> str:
        return self.organization_owned.name

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=(
                              Q(organization_owner__isnull=False) &
                              Q(person_owner__isnull=True)
                      ) | (
                              Q(organization_owner__isnull=True) &
                              Q(person_owner__isnull=False)
                      ),
                name='only_one_kind_of_owner',
            )
        ]

    @property
    def percentage(self) -> float:
        """
        % that represent over the total of the organization's shares
        """
        return 100 * self.amount / self.organization_owned.total_shares

    def save_in_ro_db(self) -> None:
        """
        This function transform the WriteOnly DB Record and save it into ReadOnly DB.

        1. This function transforms all the Django ORM objects to Python's dict
        2. This function checks if the organization exists in the RO DB
        3. If exists it updates the record otherwise it will add a new one.
        """
        share_data = {
            "share_class": self.share_class,
            "amount": self.amount,
        }

        organization_data = prepare_data_for_read_only_db(self.organization_owned)
        organization_data.update({
            "total_shares": self.organization_owned.total_shares,
            "number_of_owners": self.organization_owned.number_of_owners,
            "number_of_holdings": self.organization_owned.number_of_holdings,
            "has_foreign_owners": self.organization_owned.has_foreign_owners,
            "has_multiple_share_class": self.organization_owned.has_multiple_share_class,
        })

        organization_owner = prepare_data_for_read_only_db(self.organization_owner) if self.organization_owner else None
        person_owner = prepare_data_for_read_only_db(self.person_owner) if self.person_owner else None

        rodb = ReadOnlyDB()

        data = rodb.find_organization_element({"_id": self.organization_owned.pk})

        if organization_owner:
            organization_owner.update(share_data)
            organization_owner.update({"percentage": self.percentage})
        else:
            person_owner.update(share_data)
            person_owner.update({"percentage": self.percentage})

        if not data:
            organization_data["organizations_owner"] = [organization_owner] if organization_owner else []
            organization_data["persons_owner"] = [person_owner] if person_owner else []
            rodb.add_new_organization_share(organization_data)
        else:
            organization_data["organizations_owner"] = data["organizations_owner"]
            if organization_owner:
                organization_data["organizations_owner"].extend([organization_owner])

            organization_data["persons_owner"] = data["persons_owner"]
            if person_owner:
                organization_data["persons_owner"].extend([person_owner])

            rodb.update_organization_element({"_id": self.organization_owned.pk}, organization_data)
