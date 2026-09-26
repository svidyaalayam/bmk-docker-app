from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.core.validators import MinValueValidator

from core.models import AuditModel
from school.storage import (
    select_homework_storage,
    session_material_upload_to,
    student_homework_upload_to,
)

User = get_user_model()


class SchoolSettings(models.Model):
    """Singleton deployment-wide school settings edited in Django admin."""

    class LessonApp(models.TextChoices):
        SIKSHAVAHINI = 'sikshavahini', 'Sikshavahini'
        SUNAADAM = 'sunaadam', 'Sunaadam'

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

    school_slug = models.CharField(max_length=100, default='school')
    school_number = models.PositiveIntegerField(default=1, unique=True)
    lesson_app = models.CharField(
        max_length=20,
        choices=LessonApp.choices,
        default=LessonApp.SIKSHAVAHINI,
    )
    school_name = models.CharField(max_length=200, default='Online School')
    logo = models.ImageField(
        upload_to='school_logos/%Y/%m/',
        blank=True,
        null=True,
        help_text='School logo shown in the site header and school pages.',
    )
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
    footer_text = models.TextField(blank=True, default='')
    terms_and_conditions = models.TextField(
        blank=True,
        default='',
        help_text='Terms shown on the sign-in page and accepted before login.',
    )
    unauthorised_absence_block_threshold = models.PositiveIntegerField(
        default=3,
        validators=[MinValueValidator(1)],
        help_text='Consecutive unauthorised absences required before a teacher can block a student.',
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'School settings'
        verbose_name_plural = 'School settings'

    def __str__(self):
        return f'{self.school_name} settings'


class DailyBirthdaySnapshot(models.Model):
    """Cached student birthdays for the school week containing a date."""

    snapshot_date = models.DateField(unique=True)
    birthday_students = models.JSONField(default=list)
    generated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-snapshot_date']

    def __str__(self):
        return f'Birthdays for {self.snapshot_date}'


class Announcement(AuditModel):
    """An optional, date-windowed notice shown on the public homepage."""

    title = models.CharField(max_length=200)
    message = models.TextField(blank=True)
    image = models.ImageField(
        upload_to='announcements/%Y/%m/',
        blank=True,
        null=True,
        storage=select_homework_storage,
        help_text='Optional poster, calendar, flyer, or other visual notice.',
    )
    start_date = models.DateField(
        null=True,
        blank=True,
        help_text='Optional. The notice is shown from this date.',
    )
    end_date = models.DateField(
        null=True,
        blank=True,
        help_text='Optional. The notice is shown through this date.',
    )
    display_order = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ['display_order', '-created_at', 'id']

    def clean(self):
        if self.start_date and self.end_date and self.end_date < self.start_date:
            raise ValidationError('End date cannot be before start date.')
        if not self.message.strip() and not self.image:
            raise ValidationError('Add a message or an image to the announcement.')

    def __str__(self):
        return self.title


class AcademicCalendarEntry(AuditModel):
    class EntryType(models.TextChoices):
        WEEK = 'WEEK', 'Teaching week'
        EXAM_WEEK = 'EXAM_WEEK', 'Exam week'
        HOLIDAY = 'HOLIDAY', 'Holiday'

    term = models.ForeignKey(
        'AcademicTerm',
        on_delete=models.CASCADE,
        related_name='calendar_entries',
        null=True,
        blank=True,
    )
    entry_type = models.CharField(max_length=12, choices=EntryType.choices)
    title = models.CharField(max_length=200)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    display_order = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ['display_order', 'start_date', 'title', 'id']

    def clean(self):
        if self.entry_type != self.EntryType.HOLIDAY and (
            self.start_date is None or self.end_date is None
        ):
            raise ValidationError('Teaching and exam weeks require start and end dates.')
        if self.start_date and self.end_date and self.end_date < self.start_date:
            raise ValidationError('End date cannot be before start date.')

    def __str__(self):
        return f'{self.title} ({self.start_date} - {self.end_date})'


class AcademicTerm(AuditModel):
    name = models.CharField(max_length=200)
    display_order = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ['display_order', 'name']

    def __str__(self):
        return self.name


class Course(AuditModel):
    class DisplayLanguage(models.TextChoices):
        ENGLISH = 'en', 'English'
        SECONDARY = 'secondary', 'Secondary language'

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

    def __str__(self):
        return self.title


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
        BOY = 'M', 'Boy'
        GIRL = 'F', 'Girl'

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    gender = models.CharField(max_length=1, choices=Gender.choices)
    date_of_birth = models.DateField(null=True, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    parent_name = models.CharField(max_length=100, blank=True)
    parent_phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    account_blocked = models.BooleanField(
        default=False,
        help_text='Blocked students cannot access classes until an admin unblocks them.',
    )
    block_reason = models.TextField(blank=True)

    class Meta:
        ordering = ['user__last_name', 'user__first_name', 'user__username']

    def __str__(self):
        full_name = f'{self.user.first_name} {self.user.last_name}'.strip()
        return full_name or self.user.username


class Teacher(AuditModel):
    class Gender(models.TextChoices):
        MALE = 'M', 'Male'
        FEMALE = 'F', 'Female'

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='teacher_profile')
    gender = models.CharField(max_length=1, choices=Gender.choices)
    phone = models.CharField(max_length=20, blank=True)

    class Meta:
        ordering = ['user__last_name', 'user__first_name', 'user__username']

    def __str__(self):
        full_name = f'{self.user.first_name} {self.user.last_name}'.strip()
        return full_name or self.user.username


class TeachingClass(AuditModel):
    """A teaching cohort managed by school admins (separate from curriculum CourseClass)."""

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    teacher_1 = models.ForeignKey(
        Teacher,
        on_delete=models.PROTECT,
        related_name='classes_as_primary',
    )
    teacher_2 = models.ForeignKey(
        Teacher,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='classes_as_secondary',
    )
    students = models.ManyToManyField(
        Student,
        through='ClassMembership',
        related_name='teaching_classes',
        blank=True,
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Teaching class'
        verbose_name_plural = 'Teaching classes'

    def __str__(self):
        return self.name


class ClassMembership(AuditModel):
    teaching_class = models.ForeignKey(
        TeachingClass,
        on_delete=models.CASCADE,
        related_name='memberships',
    )
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='class_memberships',
    )

    class Meta:
        unique_together = ('teaching_class', 'student')
        ordering = ['student__user__first_name', 'student__user__username']

    def __str__(self):
        return f'{self.student} in {self.teaching_class.name}'


class ClassSession(AuditModel):
    """One calendar date / session for a teaching class."""

    teaching_class = models.ForeignKey(
        TeachingClass,
        on_delete=models.CASCADE,
        related_name='sessions',
    )
    session_date = models.DateField()
    classwork = models.TextField(blank=True)
    homework = models.TextField(blank=True)
    is_started = models.BooleanField(default=False)
    started_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['session_date', 'id']
        unique_together = ('teaching_class', 'session_date')

    def __str__(self):
        return f'{self.teaching_class.name} @ {self.session_date}'


class ClassSessionMaterial(AuditModel):
    """Teacher-provided classwork or homework files for a session."""

    class Kind(models.TextChoices):
        CLASSWORK = 'CLASSWORK', 'Classwork'
        HOMEWORK = 'HOMEWORK', 'Homework'

    session = models.ForeignKey(
        ClassSession,
        on_delete=models.CASCADE,
        related_name='materials',
    )
    kind = models.CharField(max_length=16, choices=Kind.choices)
    file = models.FileField(
        upload_to=session_material_upload_to,
        storage=select_homework_storage,
        blank=True,
    )
    original_filename = models.CharField(max_length=255, blank=True)
    content_type = models.CharField(max_length=100, blank=True)
    storage_backend = models.CharField(
        max_length=32,
        default='local',
        help_text='local or azure_blob',
    )
    storage_uri = models.CharField(
        max_length=1000,
        blank=True,
        help_text='Blob URL or local media path reference.',
    )

    class Meta:
        ordering = ['kind', 'created_at', 'id']

    def __str__(self):
        return f'{self.kind} material {self.id} for session {self.session_id}'


class ClassSessionAttendance(AuditModel):
    class Status(models.TextChoices):
        NOT_MARKED = 'NOT_MARKED', 'Not marked'
        PRESENT = 'PRESENT', 'Present'
        AUTHORISED_ABSENT = 'AUTHORISED_ABSENT', 'Authorised absent'
        UNAUTHORISED_ABSENT = 'UNAUTHORISED_ABSENT', 'Unauthorised absent'

    session = models.ForeignKey(
        ClassSession,
        on_delete=models.CASCADE,
        related_name='attendance_records',
    )
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='session_attendance',
    )
    status = models.CharField(
        max_length=32,
        choices=Status.choices,
        default=Status.NOT_MARKED,
    )
    homework_submitted = models.BooleanField(
        default=False,
        help_text='Student-declared homework submission for this session.',
    )

    class Meta:
        unique_together = ('session', 'student')
        ordering = ['student__user__first_name', 'student__user__username']

    def __str__(self):
        return f'{self.student} — {self.session} ({self.status})'


class ClassSessionComment(AuditModel):
    """Comment on a session+student calendar item (teacher or that student)."""

    session = models.ForeignKey(
        ClassSession,
        on_delete=models.CASCADE,
        related_name='comments',
    )
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='session_comments',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='class_session_comments',
    )
    body = models.TextField()

    class Meta:
        ordering = ['created_at', 'id']

    def __str__(self):
        return f'Comment by {self.author_id} on session {self.session_id} student {self.student_id}'


class ClassSessionHomework(AuditModel):
    """Homework submission for a session+student. Local or Azure Blob."""

    session = models.ForeignKey(
        ClassSession,
        on_delete=models.CASCADE,
        related_name='homework_submissions',
    )
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='homework_submissions',
    )
    file = models.FileField(
        upload_to=student_homework_upload_to,
        storage=select_homework_storage,
        blank=True,
    )
    original_filename = models.CharField(max_length=255, blank=True)
    content_type = models.CharField(max_length=100, blank=True)
    storage_backend = models.CharField(
        max_length=32,
        default='local',
        help_text='local or azure_blob',
    )
    storage_uri = models.CharField(
        max_length=1000,
        blank=True,
        help_text='Stable blob/object name or local media path (not a SAS URL).',
    )
    teacher_feedback = models.TextField(blank=True)
    ai_evaluation_status = models.CharField(
        max_length=32,
        blank=True,
        default='',
        help_text='Future: pending | done | skipped',
    )
    ai_evaluation_notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at', 'id']

    def __str__(self):
        return f'Homework {self.id} — session {self.session_id} student {self.student_id}'


class AdminRequest(models.Model):
    class Kind(models.TextChoices):
        REQUEST = 'REQUEST', 'Request'
        FEEDBACK = 'FEEDBACK', 'Feedback / suggestion'

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='admin_requests')
    kind = models.CharField(max_length=16, choices=Kind.choices)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    reply = models.TextField(blank=True)
    replied_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='admin_request_replies')
    resolved = models.BooleanField(default=False)
    resolved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at', '-id']


class StudentTeacherRequest(models.Model):
    class Kind(models.TextChoices):
        REQUEST = 'REQUEST', 'Request'
        FEEDBACK = 'FEEDBACK', 'Feedback / suggestion'

    teaching_class = models.ForeignKey(TeachingClass, on_delete=models.CASCADE, related_name='student_teacher_requests')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='teacher_requests')
    kind = models.CharField(max_length=16, choices=Kind.choices)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    reply = models.TextField(blank=True)
    replied_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='student_teacher_request_replies')
    resolved = models.BooleanField(default=False)
    resolved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at', '-id']
