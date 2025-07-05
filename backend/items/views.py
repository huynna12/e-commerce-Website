# views.py

from rest_framework import generics
from .models import Item
from .serializers import ItemDetailSerializer
from rest_framework.permissions import AllowAny

class ItemDetailView(generics.RetrieveAPIView):
    queryset = Item.objects.all()
    serializer_class = ItemDetailSerializer
    lookup_field = 'pk'  # or use 'pk'
    permission_classes = [AllowAny]  # Adjust permissions as needed