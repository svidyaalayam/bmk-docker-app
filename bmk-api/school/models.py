from django.contrib.auth import get_user_model
from django.db import models

from core.models import AuditModel

User = get_user_model()


class School(models.Model):
    """A tenant school in the multi-school platform."""

    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=100, unique=True)
    domain = models.CharField(
        max_length=255,
        blank=True,
        help_text='Optional custom domain, e.g. balamukundam.org',
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class SchoolSettings(models.Model):
    """Per-school homepage/content settings edited in Django admin."""

    class SecondaryLanguage(models.TextChoices):
        NONE = '', 'None'
        HINDI = 'hi', 'Hindi'
        TELUGU = 'te', 'Telugu'
        TAMIL = 'ta', 'Tamil'
        KANNADA = 'kn', 'Kannada'
        MALAYALAM = 'ml', 'Malayalam'
        MARATHI = 'mr', 'Marathi'
        GUJARATI = 'gu', 'Gujarati'
        BENGALI = 'bn', 'Bengali'
        PUNJABI = 'pa', 'Punjabi'
        ODIA = 'or', 'Odia'
        ASSAMESE = 'as', 'Assamese'
        URDU = 'ur', 'Urdu'
        SANSKRIT = 'sa', 'Sanskrit'
        NEPALI = 'ne', 'Nepali'
        ARABIC = 'ar', 'Arabic'
        SPANISH = 'es', 'Spanish'
        FRENCH = 'fr', 'French'
        GERMAN = 'de', 'German'
        PORTUGUESE = 'pt', 'Portuguese'
        CHINESE = 'zh', 'Chinese'
        JAPANESE = 'ja', 'Japanese'
        KOREAN = 'ko', 'Korean'
        RUSSIAN = 'ru', 'Russian'
        INDONESIAN = 'id', 'Indonesian'
        VIETNAMESE = 'vi', 'Vietnamese'

    school = models.OneToOneField(School, on_delete=models.CASCADE, related_name='settings')
    school_name = models.CharField(max_length=200, default='Online School')
    tagline = models.CharField(max_length=255, blank=True, default='')
    introduction = models.TextField(
        blank=True,
        help_text='Primary introduction shown on the public homepage (usually English).',
    )
    secondary_language = models.CharField(
        max_length=5,
        choices=SecondaryLanguage.choices,
        blank=True,
        default=SecondaryLanguage.NONE,
        help_text='Optional second language/script for the introduction.',
    )
    introduction_secondary = models.TextField(
        blank=True,
        help_text='Introduction text in the selected secondary language.',
    )
    footer_text = models.CharField(max_length=255, blank=True, default='')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'School settings'
        verbose_name_plural = 'School settings'

    def __str__(self):
        return f'{self.school_name} settings'


class Course(AuditModel):
    class DisplayLanguage(models.TextChoices):
        ENGLISH = 'en', 'English'
        SECONDARY = 'secondary', 'Secondary language'

    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='courses')
    title = models.CharField(max_length=200)
    summary = models.TextField(blank=True)
    display_order = models.PositiveIntegerField(default=0)
    display_language = models.CharField(
        max_length=20,
        choices=DisplayLanguage.choices,
        default=DisplayLanguage.ENGLISH,
        help_text=(
            'Show this course in English or in the school secondary language '
            '(configured under School settings).'
        ),
    )
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ['display_order', 'title']
        unique_together = ('school', 'title')

    def __str__(self):
        return f'{self.school.name} — {self.title}'


class CourseClass(AuditModel):
    """A class/level within a course (e.g. Seshadri under Telugu)."""

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='classes')
    name = models.CharField(max_length=200)
    display_order = models.PositiveIntegerField(default=0)
    aim = models.TextField(blank=True, help_text='Aim / learning goals for this class.')
    conditions = models.TextField(
        blank=True,
        help_text='Entry conditions, prerequisites, or eligibility for this class.',
    )
    curriculum = models.TextField(
        blank=True,
        help_text='Curriculum content taught in this class.',
    )
    aim_secondary = models.TextField(
        blank=True,
        help_text='Aim in the school secondary language.',
    )
    conditions_secondary = models.TextField(
        blank=True,
        help_text='Conditions/rules in the school secondary language.',
    )
    curriculum_secondary = models.TextField(
        blank=True,
        help_text='Curriculum in the school secondary language.',
    )
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ['display_order', 'name']
        verbose_name = 'Class'
        verbose_name_plural = 'Classes'
        unique_together = ('course', 'name')

    def __str__(self):
        return f'{self.course.title} — {self.name}'


class Student(AuditModel):
    class Gender(models.TextChoices):
        MALE = 'M', 'Male'
        FEMALE = 'F', 'Female'
        OTHER = 'O', 'Other'

    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='students')
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    gender = models.CharField(max_length=1, choices=Gender.choices)
    date_of_birth = models.DateField(null=True, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    parent_name = models.CharField(max_length=100, blank=True)
    parent_phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['user__last_name', 'user__first_name', 'user__username']

    def __str__(self):
        full_name = f'{self.user.first_name} {self.user.last_name}'.strip()
        return full_name or self.user.username


class Teacher(AuditModel):
    class Gender(models.TextChoices):
        MALE = 'M', 'Male'
        FEMALE = 'F', 'Female'
        OTHER = 'O', 'Other'

    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='teachers')
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='teacher_profile')
    gender = models.CharField(max_length=1, choices=Gender.choices)
    phone = models.CharField(max_length=20, blank=True)

    class Meta:
        ordering = ['user__last_name', 'user__first_name', 'user__username']

    def __str__(self):
        full_name = f'{self.user.first_name} {self.user.last_name}'.strip()
        return full_name or self.user.username
