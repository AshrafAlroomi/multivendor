from rest_framework import generics
from .models import SpecialDeal, SpecialDealItem
from .serializers import SpecialDealSerializer,SpecialDealItemSerializer
from rest_framework import permissions


class SpecialDealList(generics.ListCreateAPIView):
    queryset = SpecialDeal.objects.all()
    serializer_class = SpecialDealSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        return SpecialDeal.objects.filter(owner=user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class SpecialDealDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = SpecialDeal.objects.all()
    serializer_class = SpecialDealSerializer

    def perform_update(self, serializer):
        serializer.save(owner=self.request.user)


from datetime import date


class SpecialDealAllList(generics.ListAPIView):
    serializer_class = SpecialDealSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        today = date.today()
        queryset = SpecialDeal.objects.filter(active=True, valid_to__gte=today)  #
        # username = self.request.query_params.get('username')
        # if username is not None:
        #     queryset = queryset.filter(purchaser__username=username)
        return queryset



class SpecialDealItemsList(generics.ListCreateAPIView):
    queryset = SpecialDealItem.objects.all()
    serializer_class = SpecialDealItemSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        return SpecialDealItem.objects.filter(owner=user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class SpecialDealItemsDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = SpecialDealItem.objects.all()
    serializer_class = SpecialDealItemSerializer 

    def perform_update(self, serializer):
        serializer.save(owner=self.request.user)

