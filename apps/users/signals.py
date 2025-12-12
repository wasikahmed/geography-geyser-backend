import requests
from django.core.files.base import ContentFile
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

        # get profile image
        picture_url = data.get('picture')

        # only download if the user doesn't already have an image and a URL exists
        if picture_url and not user.profile_image:
            try:
                response = requests.get(picture_url)
                if response.status_code == 200:
                    file_name = f"profile_{user.id}.jpg"

                    # save the image to the field (uploads to cloudinary automatically)
                    user.profile_image.save(
                        file_name,
                        ContentFile(response.content),
                        save=False # save explicitly at the end
                    )
            except Exception as e:
                print(f"Failed to download google profile image: {e}")

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