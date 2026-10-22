from django.conf import settings
from django.contrib import admin, messages
from django.core.mail import send_mass_mail
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.urls import path, reverse
from django.utils import timezone
from django.utils.html import format_html
from django.db.models import Q
from django.contrib.auth import get_user_model

from .models import (
    AcademicCalendarEntry,
    AcademicTerm,
    Announcement,
    ClassMembership,
    ClassSession,
    ClassSessionAttendance,
    ClassSessionComment,
    ClassSessionHomework,
    ClassSessionMaterial,
    Course,
    CourseClass,
    DailyBirthdaySnapshot,
    SchoolSettings,
    Student,
    Teacher,
    TeachingClass,
)

User = get_user_model()


@admin.register(SchoolSettings)
class SchoolSettingsAdmin(admin.ModelAdmin):
    list_display = (
        'school_name', 'school_slug', 'lesson_app', 'open_student_registration',
        'secondary_language', 'updated_at',
    )
    list_filter = ('secondary_language', 'lesson_app')
    search_fields = ('school_name', 'school_slug')
    fieldsets = (
        ('School', {
            'fields': ('school_name', 'school_slug', 'school_number', 'lesson_app', 'logo', 'tagline', 'footer_text'),
        }),
        ('Introduction page', {
            'fields': ('introduction', 'secondary_language', 'introduction_secondary'),
        }),
        ('Registration', {
            'fields': ('open_student_registration',),
            'description': 'Teacher registration is always open.',
        }),
        ('Student account blocking', {
            'fields': ('unauthorised_absence_block_threshold',),
        }),
        ('Sign-in terms and conditions', {
            'fields': ('terms_and_conditions',),
        }),
    )


@admin.register(DailyBirthdaySnapshot)
class DailyBirthdaySnapshotAdmin(admin.ModelAdmin):
    list_display = ('snapshot_date', 'birthday_count', 'generated_at')
    ordering = ('-snapshot_date',)
    readonly_fields = ('snapshot_date', 'birthday_students', 'generated_at')

    @admin.display(description='Birthday students')
    def birthday_count(self, obj):
        return len(obj.birthday_students or [])


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    change_form_template = 'admin/school/announcement/change_form.html'
    list_display = ('title', 'start_date', 'end_date', 'is_published', 'email_status', 'display_order')
    list_filter = ('is_published',)
    search_fields = ('title', 'message')
    ordering = ('display_order', '-created_at', 'id')
    fieldsets = (
        ('Announcement', {
            'fields': ('title', 'message', 'image'),
        }),
        ('Visibility', {
            'fields': ('start_date', 'end_date', 'is_published', 'display_order'),
        }),
        ('Email delivery', {
            'fields': ('email_sent_at', 'email_sent_by', 'email_recipient_count'),
            'description': 'Use “Send announcement email” after saving this announcement.',
        }),
    )
    readonly_fields = ('email_sent_at', 'email_sent_by', 'email_recipient_count')

    @admin.display(description='Email delivery')
    def email_status(self, obj):
        if not obj.email_sent_at:
            return 'Not sent'
        return f'Sent to {obj.email_recipient_count} on {obj.email_sent_at:%d %b %Y %H:%M}'

    def get_urls(self):
        return [
            path(
                '<int:announcement_id>/send-email/',
                self.admin_site.admin_view(self.send_email_view),
                name='school_announcement_send_email',
            ),
        ] + super().get_urls()

    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        extra_context = extra_context or {}
        if object_id:
            url = reverse('admin:school_announcement_send_email', args=[object_id])
            extra_context['announcement_email_url'] = url
        return super().changeform_view(request, object_id, form_url, extra_context)

    def send_email_view(self, request, announcement_id):
        announcement = get_object_or_404(Announcement, pk=announcement_id)
        recipients = User.objects.filter(is_active=True).filter(
            Q(email_verified=True) | Q(is_superuser=True)
        ).exclude(email='').values_list('email', flat=True).distinct()
        recipient_list = list(recipients)
        if request.method == 'POST':
            if not announcement.is_published:
                self.message_user(request, 'Publish the announcement before sending it by email.', messages.ERROR)
                return redirect(reverse('admin:school_announcement_change', args=[announcement.id]))
            body = announcement.message.strip() or 'A new school announcement is available in the school portal.'
            body += '\n\nPlease do not reply to this automated message.'
            email_messages = [(announcement.title, body, settings.DEFAULT_FROM_EMAIL, [email]) for email in recipient_list]
            try:
                sent_count = send_mass_mail(email_messages, fail_silently=False) if email_messages else 0
            except Exception:
                self.message_user(request, 'Email sending failed. No delivery record was saved; check the mail configuration and try again.', messages.ERROR)
                return redirect(reverse('admin:school_announcement_change', args=[announcement.id]))
            announcement.email_sent_at = timezone.now()
            announcement.email_sent_by = request.user
            announcement.email_recipient_count = sent_count
            announcement.save(update_fields=('email_sent_at', 'email_sent_by', 'email_recipient_count', 'updated_at'))
            self.message_user(request, f'Announcement email sent individually to {sent_count} recipient(s).', messages.SUCCESS)
            return redirect(reverse('admin:school_announcement_change', args=[announcement.id]))
        context = {
            **self.admin_site.each_context(request),
            'title': 'Send announcement email',
            'announcement': announcement,
            'recipient_count': len(recipient_list),
            'opts': self.model._meta,
        }
        return TemplateResponse(request, 'admin/school/announcement/send_email.html', context)


@admin.register(AcademicCalendarEntry)
class AcademicCalendarEntryAdmin(admin.ModelAdmin):
    list_display = ('title', 'term', 'entry_type', 'start_date', 'end_date', 'is_published', 'display_order')
    list_filter = ('entry_type', 'is_published')
    search_fields = ('title', 'notes', 'term__name')
    ordering = ('display_order', 'start_date', 'title', 'id')
    fieldsets = (
        ('Calendar entry', {
            'fields': ('term', 'entry_type', 'title', 'start_date', 'end_date', 'notes'),
        }),
        ('Homepage display', {
            'fields': ('is_published', 'display_order'),
        }),
    )


@admin.register(AcademicTerm)
class AcademicTermAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_published', 'display_order')
    list_filter = ('is_published',)
    search_fields = ('name',)
    ordering = ('display_order', 'name')


class CourseClassInline(admin.StackedInline):
    model = CourseClass
    extra = 0
    fields = (
        'name',
        'display_order',
        'is_published',
        'is_active',
        'aim',
        'conditions',
        'curriculum',
        'aim_secondary',
        'conditions_secondary',
        'curriculum_secondary',
    )
    ordering = ('display_order', 'name')
    show_change_link = True


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'display_order',
        'display_language',
        'is_published',
        'is_active',
        'updated_at',
    )
    list_editable = ('display_order', 'display_language', 'is_published')
    list_filter = ('display_language', 'is_published', 'is_active')
    search_fields = ('title', 'summary')
    ordering = ('display_order', 'title')
    inlines = [CourseClassInline]
    fieldsets = (
        (None, {
            'fields': (
                'title',
                'summary',
                'display_order',
                'display_language',
                'is_published',
                'is_active',
            ),
        }),
    )


@admin.register(CourseClass)
class CourseClassAdmin(admin.ModelAdmin):
    list_display = ('name', 'course', 'display_order', 'is_published', 'is_active', 'updated_at')
    list_editable = ('display_order', 'is_published')
    list_filter = ('course', 'is_published', 'is_active')
    search_fields = (
        'name',
        'aim',
        'conditions',
        'curriculum',
        'aim_secondary',
        'conditions_secondary',
        'curriculum_secondary',
        'course__title',
    )
    autocomplete_fields = ('course',)
    ordering = ('course__display_order', 'display_order', 'name')
    fieldsets = (
        (None, {
            'fields': ('course', 'name', 'display_order', 'is_published', 'is_active'),
        }),
        ('Class details (primary language)', {
            'fields': ('aim', 'conditions', 'curriculum'),
        }),
        ('Class details (secondary language)', {
            'fields': ('aim_secondary', 'conditions_secondary', 'curriculum_secondary'),
        }),
    )


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('user', 'gender', 'phone', 'parent_name', 'is_active', 'created_at')
    list_filter = ('gender', 'is_active')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'parent_name')
    raw_id_fields = ('user', 'created_by', 'updated_by')


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('user', 'gender', 'phone', 'is_active', 'created_at')
    list_filter = ('gender', 'is_active')
    search_fields = ('user__username', 'user__first_name', 'user__last_name')
    raw_id_fields = ('user', 'created_by', 'updated_by')


class ClassMembershipInline(admin.TabularInline):
    model = ClassMembership
    extra = 0
    raw_id_fields = ('student', 'created_by', 'updated_by')


class ClassSessionInline(admin.TabularInline):
    model = ClassSession
    extra = 0
    fields = ('session_date', 'classwork', 'homework', 'is_started', 'started_at')
    readonly_fields = ('is_started', 'started_at')


@admin.register(TeachingClass)
class TeachingClassAdmin(admin.ModelAdmin):
    list_display = ('name', 'teacher_1', 'teacher_2', 'is_active', 'updated_at')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')
    raw_id_fields = ('teacher_1', 'teacher_2', 'created_by', 'updated_by')
    inlines = [ClassMembershipInline, ClassSessionInline]


@admin.register(ClassSession)
class ClassSessionAdmin(admin.ModelAdmin):
    list_display = ('teaching_class', 'session_date', 'is_started', 'started_at')
    list_filter = ('is_started',)
    raw_id_fields = ('teaching_class', 'created_by', 'updated_by')


@admin.register(ClassSessionAttendance)
class ClassSessionAttendanceAdmin(admin.ModelAdmin):
    list_display = ('session', 'student', 'status', 'updated_at')
    list_filter = ('status',)
    raw_id_fields = ('session', 'student', 'created_by', 'updated_by')


@admin.register(ClassSessionComment)
class ClassSessionCommentAdmin(admin.ModelAdmin):
    list_display = ('session', 'student', 'author', 'created_at')
    raw_id_fields = ('session', 'student', 'author', 'created_by', 'updated_by')


@admin.register(ClassSessionHomework)
class ClassSessionHomeworkAdmin(admin.ModelAdmin):
    list_display = ('session', 'student', 'original_filename', 'storage_backend', 'created_at')
    raw_id_fields = ('session', 'student', 'created_by', 'updated_by')


@admin.register(ClassSessionMaterial)
class ClassSessionMaterialAdmin(admin.ModelAdmin):
    list_display = ('session', 'kind', 'original_filename', 'storage_backend', 'created_at')
    list_filter = ('kind', 'storage_backend')
    raw_id_fields = ('session', 'created_by', 'updated_by')
