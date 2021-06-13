from django.http import JsonResponse

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.status import HTTP_201_CREATED, HTTP_404_NOT_FOUND

from .serializers import OrganizationSerializer, PersonSerializer, ShareSerializer
from .read_only import ReadOnlyDB


class OrganizationViewSet(APIView):
    """
    Add a new organization to the database
    """
    def post(self, request, *args, **kwargs):
        serializer = OrganizationSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return JsonResponse(serializer.data, status=HTTP_201_CREATED)


class PersonViewSet(APIView):
    """
    Add a new person to the database
    """
    def post(self, request, *args, **kwargs):
        serializer = PersonSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return JsonResponse(serializer.data, status=HTTP_201_CREATED)


class ShareViewSet(APIView):
    """
    Add a new share to the database
    """
    def post(self, request, *args, **kwargs):
        serializer = ShareSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return JsonResponse(serializer.data, status=HTTP_201_CREATED)


class ShareOwnersViewSet(APIView):
    """
    Get information about the owners of the organization
    """
    def get(self, request, orgnr):
        rodb = ReadOnlyDB()
        data = rodb.find_organization_element({"_id": orgnr})

        if not data:
            return Response(status=HTTP_404_NOT_FOUND)

        else:
            return JsonResponse(
                {
                    "organizations_owner": data["organizations_owner"],
                    "persons_owner": data["persons_owner"]
                }
            )


class ShareHoldingViewSet(APIView):
    """
    Get information about the shares that the organization bought
    """
    def get(self, request, orgnr):
        rodb = ReadOnlyDB()
        data = [x for x in rodb.find_organizations_element({"organizations_owner": {"$elemMatch": {"_id": orgnr}}})]

        if not data:
            return Response(status=HTTP_404_NOT_FOUND)
        else:
            return JsonResponse(data, safe=False)


class OrganizationSummaryViewSet(APIView):
    """
    Organization's summary
    """
    def get(self, request, orgnr):
        rodb = ReadOnlyDB()
        data = rodb.find_organization_element({"_id": orgnr})

        if not data:
            return Response(status=HTTP_404_NOT_FOUND)
        else:
            return JsonResponse({
                "number_of_owners": data["number_of_owners"],
                "number_of_holdings": data["number_of_holdings"],
                "has_foreign_owners": data["has_foreign_owners"],
                "has_multiple_share_class": data["has_multiple_share_class"],
            })
