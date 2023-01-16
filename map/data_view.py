from map.serializer import DiscountDataSerializer
from map.models import DiscountData
from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser

class DiscountDataAPI(viewsets.ModelViewSet):
    serializer_class = DiscountDataSerializer
    queryset = DiscountData.objects.all()
    permission_classes = [IsAdminUser]

    """
    Example empty viewset demonstrating the standard
    actions that will be handled by a router class.

    If you're using format suffixes, make sure to also include
    the `format=None` keyword argument for each action.
    """

    # def list(self, request):
    #     pass

    # def create(self, request):
    #     pass

    # def retrieve(self, request, pk=None):
    #     pass

    # def update(self, request, pk=None):
    #     pass

    # def partial_update(self, request, pk=None):
    #     pass

    # def destroy(self, request, pk=None):
    #     pass
    