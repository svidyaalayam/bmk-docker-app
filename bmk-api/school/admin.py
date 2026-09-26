from django.contrib import admin

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


@admin.register(SchoolSettings)
class SchoolSettingsAdmin(admin.ModelAdmin):
    list_display = ('school_name', 'school_slug', 'lesson_app', 'secondary_language', 'updated_at')
    list_filter = ('secondary_language', 'lesson_app')
    search_fields = ('school_name', 'school_slug')
    fieldsets = (
        ('School', {
            'fields': ('school_name', 'school_slug', 'school_number', 'lesson_app', 'logo', 'tagline', 'footer_text'),
        }),
        ('Introduction page', {
            'fields': ('introduction', 'secondary_language', 'introduction_secondary'),
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
    list_display = ('title', 'start_date', 'end_date', 'is_published', 'display_order')
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
    )


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
