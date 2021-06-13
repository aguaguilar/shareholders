from django.urls import path

from .views import (
    OrganizationViewSet,
    PersonViewSet,
    ShareViewSet,
    ShareOwnersViewSet,
    ShareHoldingViewSet,
    OrganizationSummaryViewSet
)


urlpatterns = [
    path('organization/', OrganizationViewSet.as_view()),
    path('person/', PersonViewSet.as_view()),
    path('share/', ShareViewSet.as_view()),
    path('<int:orgnr>/owners', ShareOwnersViewSet.as_view()),
    path('<int:orgnr>/holding', ShareHoldingViewSet.as_view()),
    path('<int:orgnr>/summary', OrganizationSummaryViewSet.as_view()),
]
