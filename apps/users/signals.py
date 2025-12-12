from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

# Import the signal from allauth
from allauth.account.signals import user_signed_up

User = get_user_model()


@receiver(post_save, sender=User)
def assign_group_to_superuser(sender, instance, created, **kwargs):
    if created and instance.is_superuser:
        admin_group, _ = Group.objects.get_or_create(name='Admin')
        instance.groups.add(admin_group)


@receiver(user_signed_up)
def populate_profile(request, user, **kwargs):
    """
    Used for Social Auth (Google) signals.
    1. Assign 'Student' group to new social users.
    2. Extract 'full_name' from Google profile.
    """
    # Assign Role (Group)
    student_group, _ = Group.objects.get_or_create(name='Student')
    user.groups.add(student_group)

    # Extract Name from Google
    # The signal passes a 'sociallogin' object in kwargs
    sociallogin = kwargs.get('sociallogin')
    
    if sociallogin and sociallogin.account.provider == 'google':
        # Google returns useful data in extra_data
        data = sociallogin.account.extra_data
        
        
        # get first name (given_name) and last name (family_name)
        first_name = data.get('given_name', '')
        last_name = data.get('family_name', '')

        user.first_name = first_name
        user.last_name = last_name
        user.save()
        
        # If 'name' is missing, try combining given_name + family_name
        # if not google_name:
        #     given_name = data.get('given_name', '')
        #     family_name = data.get('family_name', '')
        #     google_name = f"{given_name} {family_name}".strip()

        # # Save it to your custom User model
        # if google_name:
        #     user.full_name = google_name
        #     user.save()