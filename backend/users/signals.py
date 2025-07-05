from django.db.models.signals import post_save 
from django.contrib.auth.models import User #The user model
from django.dispatch import receiver     # Receive signals and perform actions
from .models import Profile # The profile model

@receiver(post_save, sender=User)  # Listen for the post_save signal from the User model
# Function to create a profile when a user is created
def build_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)  # Listen for the post_save signal from the User model
def save_profile(sender, instance, **kwargs):
    instance.profile.save()