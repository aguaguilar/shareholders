from django.db import models
from django.db.models import Q


class Entity:
    name = models.CharField(max_length=255, null=False, blank=False)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=255)


class Person(Entity, models.Model):
    birth_date = models.DateField()


class Organization(Entity, models.Model):
    orgnr = models.IntegerField(primary_key=True)


class Share(models.Model):
    SHARE_CLASS_CHOICES = [
        ("A-aksjer", "A-aksjer"),
        ("B-aksje", "B-aksje"),
    ]

    organization_owner = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="organization_owned_shares"
    )
    person_owner = models.ForeignKey(
        Person,
        on_delete=models.CASCADE,
        related_name="person_owned_shares"
    )
    organization_owned = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="owner_shares"
    )
    share_class = models.CharField(choices=SHARE_CLASS_CHOICES, max_length=8)
    amount = models.IntegerField(default=0)

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
