from django.contrib import admin
from .models import Item, Review, Promotion
from .models.item import ItemImage

# Register your models here.
admin.site.register(ItemImage)
admin.site.register(Promotion)
admin.site.register(Item)
admin.site.register(Review)
