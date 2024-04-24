from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import IntegrityError

from .models import (
    UniversityUser,
    SuperAdminProfile,
    DepartmentAdminProfile,
)


@receiver(post_save, sender=UniversityUser)
def create_profile(sender, instance, created, **kwargs):
    if created:
        try:
            if instance.role == "SA":
                SuperAdminProfile.objects.create(user=instance)
            elif instance.role == "DA":
                DepartmentAdminProfile.objects.create(user=instance)
        except IntegrityError:
            print("Error creating profile: Potential data integrity issue.")
