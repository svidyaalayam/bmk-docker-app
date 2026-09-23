import json
from datetime import timezone as datetime_timezone

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from .models import SchoolSettings, Student
from .tenancy import resolve_school
from authentication.usernames import username_for_school_email


User = get_user_model()


class ResolveSchoolTests(TestCase):
    def test_returns_singleton_school_settings(self):
        settings = SchoolSettings.objects.create(
            school_slug='uk-telugu',
            school_number=1,
            school_name='UK Telugu',
        )
        self.assertEqual(resolve_school(required=True), settings)


class FirebaseUserImportViewTests(TestCase):
    def setUp(self):
        self.school = SchoolSettings.objects.create(
            school_name='Test School',
            school_slug='test-school',
            school_number=1,
        )
        self.admin = User.objects.create_user(
            username='admin@example.com',
            email='admin@example.com',
            password='test-password',
            role=User.Roles.ADMIN,
        )
        self.client = APIClient()
        self.client.force_authenticate(self.admin)

    def upload(self, records, skip_duplicates=False):
        uploaded_file = SimpleUploadedFile(
            'firebase-users.json',
            json.dumps(records).encode(),
            content_type='application/json',
        )
        url = '/api/users/import/?duplicate_action=skip' if skip_duplicates else '/api/users/import/'
        return self.client.post(url, {'file': uploaded_file}, format='multipart')

    def test_imports_firebase_student_and_preserves_account_state(self):
        response = self.upload(
            [
                {
                    'uid': '038046mLu2YVOa9eQjWwRK42k4d2',
                    'email': 'ssmaruvada@gmail.com',
                    'auth': {
                        'displayName': None,
                        'phoneNumber': None,
                        'disabled': False,
                        'emailVerified': True,
                        'creationTime': 'Tue, 03 Sep 2024 19:02:54 GMT',
                        'lastSignInTime': 'Wed, 04 Sep 2024 09:12:10 GMT',
                    },
                    'firestore': {
                        'loginid': 'ssmaruvada@gmail.com',
                        'gender': 'Boy',
                        'contactnumber': '07711561441',
                        'accountsuspended': False,
                        'usertype': 0,
                        'parentsname': 'Parent Name',
                        'surname': 'Maruvada',
                        'dob': '',
                        'name': 'Satya Subrahmaniyam',
                    },
                }
            ]
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['created_count'], 1)
        user = User.objects.get(email='ssmaruvada@gmail.com')
        self.assertEqual(user.username, username_for_school_email(user.email, self.school))
        self.assertEqual(user.username, user.email)
        student = Student.objects.get(user=user)
        self.assertEqual(user.legacy_uid, '038046mLu2YVOa9eQjWwRK42k4d2')
        self.assertEqual(user.role, User.Roles.STUDENT)
        self.assertTrue(user.email_verified)
        self.assertTrue(user.is_active)
        self.assertEqual(user.date_joined.year, 2024)
        self.assertEqual(user.date_joined.tzinfo, datetime_timezone.utc)
        self.assertEqual(user.last_login.year, 2024)
        self.assertFalse(user.has_usable_password())
        self.assertEqual(student.gender, Student.Gender.BOY)
        self.assertEqual(student.parent_name, 'Parent Name')

    def test_rejects_invalid_rows_without_creating_any_users(self):
        response = self.upload(
            [
                {
                    'uid': 'valid-uid',
                    'email': 'valid@example.com',
                    'auth': {'disabled': False, 'emailVerified': True},
                    'firestore': {'usertype': 0, 'gender': 'Boy', 'name': 'Valid'},
                },
                {
                    'uid': 'invalid-uid',
                    'email': 'not-an-email',
                    'auth': {'disabled': False, 'emailVerified': True},
                    'firestore': {'usertype': 0, 'gender': 'Boy', 'name': 'Invalid'},
                },
            ]
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(response.data['errors'][0]['row'], 2)

    def test_imports_admin_without_a_student_or_teacher_profile(self):
        response = self.upload(
            [
                {
                    'uid': 'admin-uid',
                    'email': 'legacy.admin@example.com',
                    'auth': {'disabled': False, 'emailVerified': True},
                    'firestore': {'usertype': 2, 'name': 'Legacy', 'surname': 'Admin'},
                }
            ]
        )

        self.assertEqual(response.status_code, 201)
        user = User.objects.get(email='legacy.admin@example.com')
        self.assertEqual(user.role, User.Roles.ADMIN)
        self.assertFalse(hasattr(user, 'student_profile'))
        self.assertFalse(hasattr(user, 'teacher_profile'))

    def test_requires_confirmation_before_skipping_duplicate_users(self):
        User.objects.create_user(
            username='existing@example.com',
            email='existing@example.com',
            password='test-password',
        )
        records = [
            {
                'uid': 'existing-uid',
                'email': 'existing@example.com',
                'auth': {'disabled': False, 'emailVerified': True},
                'firestore': {'usertype': 0, 'gender': 'Boy', 'name': 'Existing'},
            },
            {
                'uid': 'new-uid',
                'email': 'new@example.com',
                'auth': {'disabled': False, 'emailVerified': True},
                'firestore': {'usertype': 0, 'gender': 'Girl', 'name': 'New'},
            },
        ]

        confirmation = self.upload(records)
        self.assertEqual(confirmation.status_code, 409)
        self.assertEqual(confirmation.data['duplicate_count'], 1)
        self.assertFalse(User.objects.filter(email='new@example.com').exists())

        completed = self.upload(records, skip_duplicates=True)
        self.assertEqual(completed.status_code, 201)
        self.assertEqual(completed.data['created_count'], 1)
        self.assertEqual(completed.data['skipped_count'], 1)
        self.assertTrue(User.objects.filter(email='new@example.com').exists())

    def test_requires_confirmation_before_skipping_duplicate_rows_in_file(self):
        records = [
            {
                'uid': 'repeated-uid',
                'email': 'first@example.com',
                'auth': {'disabled': False, 'emailVerified': True},
                'firestore': {'usertype': 0, 'gender': 'Boy', 'name': 'First'},
            },
            {
                'uid': 'repeated-uid',
                'email': 'later-copy@example.com',
                'auth': {'disabled': False, 'emailVerified': True},
                'firestore': {'usertype': 0, 'gender': 'Boy', 'name': 'Later Copy'},
            },
        ]

        confirmation = self.upload(records)
        self.assertEqual(confirmation.status_code, 409)
        self.assertEqual(confirmation.data['duplicate_count'], 1)
        self.assertFalse(User.objects.filter(email='first@example.com').exists())

        completed = self.upload(records, skip_duplicates=True)
        self.assertEqual(completed.status_code, 201)
        self.assertEqual(completed.data['created_count'], 1)
        self.assertEqual(completed.data['skipped_count'], 1)
        self.assertTrue(User.objects.filter(email='first@example.com').exists())

    def test_rejects_an_email_that_already_exists(self):
        User.objects.create_user(
            username='shared@example.com', email='shared@example.com', password='test-password',
        )
        response = self.upload([{
            'uid': 'shared-firebase-uid', 'email': 'shared@example.com',
            'auth': {'disabled': False, 'emailVerified': True},
            'firestore': {'usertype': 0, 'gender': 'Girl', 'name': 'Shared'},
        }])
        self.assertEqual(response.status_code, 409)
        self.assertEqual(response.data['duplicate_count'], 1)

    def test_email_login_resolves_the_school_uuid_username(self):
        email = 'member@example.com'
        user = User.objects.create_user(
            username=username_for_school_email(email, self.school),
            email=email,
            password='test-password',
            email_verified=True,
            is_active=True,
        )

        self.school.school_name = 'Renamed School'
        self.school.save(update_fields=['school_name'])
        response = self.client.post(
            '/api/auth/login/',
            {'email': email, 'password': 'test-password'},
            format='json',
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['user']['id'], user.id)
        self.assertEqual(user.username, username_for_school_email(email, self.school))
