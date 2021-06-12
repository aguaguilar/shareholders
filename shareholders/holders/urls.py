from django.urls import path

from .views import OrganizationViewSet, PersonViewSet, ShareViewSet


urlpatterns = [
    path('organization/', OrganizationViewSet.as_view()),
    path('person/', PersonViewSet.as_view()),
    path('share/', ShareViewSet.as_view()),
]
