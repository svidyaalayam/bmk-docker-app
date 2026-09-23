from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Roles(models.TextChoices):
        ADMIN = 'ADMIN', 'Admin'
        TEACHER = 'TEACHER', 'Teacher'
        STUDENT = 'STUDENT', 'Student'

    role = models.CharField(
        max_length=10,
        choices=Roles.choices,
        default=Roles.STUDENT,
    )
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    email_verified = models.BooleanField(
        default=False,
        help_text='True after the user confirms their email address.',
    )
    legacy_uid = models.CharField(
        max_length=128,
        blank=True,
        null=True,
        help_text='Firebase UID retained when an account is imported from the legacy system.',
    )
    profile_locked = models.BooleanField(
        default=False,
        help_text='When True, registration details cannot be changed by the user.',
    )
    avatar = models.ImageField(
        upload_to='avatars/%Y/%m/',
        blank=True,
        null=True,
        help_text='Optional profile photo shown as the user avatar.',
    )

    @property
    def is_teacher(self):
        return self.role == self.Roles.TEACHER or self.is_staff

    @property
    def is_student(self):
        return self.role == self.Roles.STUDENT

    def __str__(self):
        return f'{self.username} ({self.role})'
