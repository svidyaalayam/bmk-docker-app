from datetime import date, timedelta

from django.db.models import Prefetch
from django.utils import timezone

from .models import ClassMembership, DailyBirthdaySnapshot, Student


def _birthday_students_for_window(snapshot_date: date) -> list[dict[str, str]]:
    window_dates = {
        snapshot_date + timedelta(days=offset)
        for offset in range(-4, 5)
    }
    window_month_days = {(item.month, item.day) for item in window_dates}
    students = (
        Student.objects.filter(
            user__is_active=True,
            account_blocked=False,
        )
        .select_related('user')
        .prefetch_related(
            Prefetch(
                'class_memberships',
                queryset=ClassMembership.objects.filter(
                    teaching_class__is_active=True,
                ).select_related('teaching_class__teacher_1__user').order_by(
                    'teaching_class__name',
                ),
            ),
        )
    )
    birthdays = []
    for student in students:
        if not student.date_of_birth:
            continue
        if (student.date_of_birth.month, student.date_of_birth.day) not in window_month_days:
            continue
        teacher = None
        memberships = list(student.class_memberships.all())
        if memberships:
            teacher_user = memberships[0].teaching_class.teacher_1.user
            teacher = (
                f'{teacher_user.first_name} {teacher_user.last_name}'.strip()
                or teacher_user.email
                or teacher_user.username
            )
        try:
            birthday_date = date(
                snapshot_date.year,
                student.date_of_birth.month,
                student.date_of_birth.day,
            )
        except ValueError:
            birthday_date = date(snapshot_date.year, 2, 28)
        birthdays.append({
            'name': (
                f'{student.user.first_name} {student.user.last_name}'.strip()
                or student.user.email
                or student.user.username
            ),
            'date': birthday_date.isoformat(),
            'teacher': teacher or 'New registration',
        })
    return sorted(birthdays, key=lambda item: item['date'])


def get_daily_birthday_snapshot(snapshot_date: date | None = None) -> DailyBirthdaySnapshot:
    snapshot_date = snapshot_date or timezone.localdate()
    snapshot, _created = DailyBirthdaySnapshot.objects.get_or_create(
        snapshot_date=snapshot_date,
        defaults={'birthday_students': _birthday_students_for_window(snapshot_date)},
    )
    return snapshot
