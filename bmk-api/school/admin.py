from django.contrib import admin

from .models import (
    ClassMembership,
    ClassSession,
    ClassSessionAttendance,
    ClassSessionComment,
    ClassSessionHomework,
    ClassSessionMaterial,
    Course,
    CourseClass,
    School,
    SchoolSettings,
    SchoolSubtype,
    SchoolType,
    Student,
    Teacher,
    TeachingClass,
)


class SchoolSettingsInline(admin.StackedInline):
    model = SchoolSettings
    can_delete = False
    extra = 0


@admin.register(SchoolType)
class SchoolTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'display_order', 'is_active')
    list_editable = ('display_order', 'is_active')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'slug')


@admin.register(SchoolSubtype)
class SchoolSubtypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'school_type', 'slug', 'display_order', 'is_active')
    list_filter = ('school_type', 'is_active')
    list_editable = ('display_order', 'is_active')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'slug', 'school_type__name')
    autocomplete_fields = ('school_type',)


@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'subtype', 'domain', 'is_active', 'updated_at')
    list_filter = ('is_active', 'subtype__school_type', 'subtype')
    search_fields = ('name', 'slug', 'domain')
    autocomplete_fields = ('subtype',)
    inlines = [SchoolSettingsInline]


@admin.register(SchoolSettings)
class SchoolSettingsAdmin(admin.ModelAdmin):
    list_display = ('school_name', 'school', 'secondary_language', 'updated_at')
    list_filter = ('secondary_language', 'school')
    search_fields = ('school_name', 'school__name', 'school__slug')
    autocomplete_fields = ('school',)
    fieldsets = (
        ('School', {
            'fields': ('school', 'school_name', 'logo', 'tagline', 'footer_text'),
        }),
        ('Introduction page', {
            'fields': ('introduction', 'secondary_language', 'introduction_secondary'),
        }),
    )


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
        'school',
        'display_order',
        'display_language',
        'is_published',
        'is_active',
        'updated_at',
    )
    list_editable = ('display_order', 'display_language', 'is_published')
    list_filter = ('school', 'display_language', 'is_published', 'is_active')
    search_fields = ('title', 'summary', 'school__name')
    autocomplete_fields = ('school',)
    ordering = ('school__name', 'display_order', 'title')
    inlines = [CourseClassInline]
    fieldsets = (
        (None, {
            'fields': (
                'school',
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
    list_filter = ('course__school', 'course', 'is_published', 'is_active')
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
    ordering = ('course__school__name', 'course__display_order', 'display_order', 'name')
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
    list_display = ('user', 'school', 'gender', 'phone', 'parent_name', 'is_active', 'created_at')
    list_filter = ('school', 'gender', 'is_active')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'parent_name')
    raw_id_fields = ('user', 'created_by', 'updated_by')
    autocomplete_fields = ('school',)


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('user', 'school', 'gender', 'phone', 'is_active', 'created_at')
    list_filter = ('school', 'gender', 'is_active')
    search_fields = ('user__username', 'user__first_name', 'user__last_name')
    raw_id_fields = ('user', 'created_by', 'updated_by')
    autocomplete_fields = ('school',)


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
    list_display = ('name', 'school', 'teacher_1', 'teacher_2', 'is_active', 'updated_at')
    list_filter = ('school', 'is_active')
    search_fields = ('name', 'description')
    autocomplete_fields = ('school',)
    raw_id_fields = ('teacher_1', 'teacher_2', 'created_by', 'updated_by')
    inlines = [ClassMembershipInline, ClassSessionInline]


@admin.register(ClassSession)
class ClassSessionAdmin(admin.ModelAdmin):
    list_display = ('teaching_class', 'session_date', 'is_started', 'started_at')
    list_filter = ('is_started', 'teaching_class__school')
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
