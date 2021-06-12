from rest_framework.serializers import ModelSerializer

from .models import Organization, Person, Share


class OrganizationSerializer(ModelSerializer):
    class Meta:
        model = Organization
        fields = ['name', 'postal_code', 'country', 'orgnr']


class PersonSerializer(ModelSerializer):
    class Meta:
        model = Person
        fields = ['name', 'postal_code', 'country', 'birth_date']


class ShareSerializer(ModelSerializer):
    class Meta:
        model = Share
        fields = ['organization_owner', 'person_owner', 'organization_owned', 'share_class', 'amount']
