from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Item


@receiver(post_save, sender=Item)
def set_profile_is_seller_on_item_create(sender, instance: Item, created: bool, **kwargs):
    if not created:
        return

    seller = getattr(instance, 'seller', None)
    if not seller:
        return

    profile = getattr(seller, 'profile', None)
    if not profile:
        # Be defensive in case user-profile creation signals weren't registered.
        from users.models import Profile

        profile, _ = Profile.objects.get_or_create(user=seller)

    if not profile.is_seller:
        profile.is_seller = True
        profile.save(update_fields=['is_seller', 'updated_at'])
