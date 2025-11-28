from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.crypto import get_random_string
from django.contrib.auth import get_user_model
from .models import Student, Professor

User = get_user_model()

@receiver(post_save, sender=User)
def create_default_credentials(sender, instance, created, **kwargs):

    if not created:
        return

    random_pass = get_random_string(length=10)
    instance.set_password(random_pass)

    if not instance.email:
        instance.email = f"{instance.username}@ucms.edu"

    instance.save()



@receiver(post_save, sender=Student)
def generate_student_email(sender, instance, created, **kwargs):

    if created:
        user = instance.user
        year = "2025"
        user.email = f"s{year}-{instance.id}@ucms.edu"
        user.save()


@receiver(post_save, sender=Professor)
def generate_professor_email(sender, instance, created, **kwargs):


    if created:
        user = instance.user
        user.email = f"p-{instance.id}@ucms.edu"
        user.save()

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.crypto import get_random_string
from django.contrib.auth import get_user_model
from .models import Student

User = get_user_model()


@receiver(post_save, sender=Student)
def generate_student_credentials(sender, instance, created, **kwargs):
    if not created:
        return

    user = instance.user

    first = (user.first_name or "").strip().lower()
    last = (user.last_name or "").strip().lower()

    if not first or not last:
        parts = user.username.lower().split(".")
        if len(parts) == 2:
            first, last = parts
        else:
            first = user.username.lower()
            last = "student"

    base_email = f"{first}.{last}@student.ucms.com"
    final_email = base_email
    counter = 1

    while User.objects.filter(email=final_email).exists():
        counter += 1
        final_email = f"{first}.{last}{counter}@student.ucms.com"

    user.email = final_email

    national_id = instance.national_id.strip()
    last4 = national_id[-4:] if len(national_id) >= 4 else national_id
    last3letters = last[:3] if len(last) >= 3 else last

    generated_password = f"{last4}{last3letters}"

    user.set_password(generated_password)

    user.save()
