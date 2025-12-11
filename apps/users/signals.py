from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

User = get_user_model()


@receiver(post_save, sender=User)
def assign_group_to_superuser(sender, instance, created, **kwargs):
    if created and instance.is_superuser:
        admin_group, _ = Group.objects.get_or_create(name='Admin')
        instance.groups.add(admin_group)