from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import GroupsViewSet, MultipleModelsCreateView

app_name = "rest_api"

routers = DefaultRouter()

routers.register("groups", GroupsViewSet)

urlpatterns = [
    path("", include(routers.urls)),
    path("update/", MultipleModelsCreateView.as_view(), name='multiply_update')
]
