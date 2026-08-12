from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from school.models import Course, CourseClass, School, SchoolSettings

User = get_user_model()


class Command(BaseCommand):
    help = 'Seed Balamukundam (Telugu) and Balavikas (Kannada) schools with demo data.'

    @transaction.atomic
    def handle(self, *args, **options):
        bmk = self._ensure_school(
            name='Balamukundam',
            slug='balamukundam',
            domain='balamukundam.localhost',
            settings={
                'school_name': 'Balamukundam',
                'tagline': 'Telugu School',
                'secondary_language': SchoolSettings.SecondaryLanguage.TELUGU,
                'introduction': (
                    'Being far away from our motherland, with the good intention of teaching our '
                    'mother tongue Telugu to our children we started this programme called Balamukundam. '
                    'In Balamukundam lessons, children learn to read, write, converse and sing songs '
                    'and poems in Telugu. They also learn moral stories.\n\n'
                    'Keeping in mind their age and proficiency of the language, children have been put '
                    'into various levels named after the seven hills of Tirumala.'
                ),
                'introduction_secondary': (
                    'మాతృదేశానికి ఎంతో దూరంలో ఉన్న మన అందరికి, మన పిల్లలకి, మన మాతృభాష నేర్పించాలనే '
                    'సత్సంకల్పంతో మొదలైనది బాలముకుందం.'
                ),
                'footer_text': 'email:bmtsuk@gmail.com',
            },
        )
        bv = self._ensure_school(
            name='Balavikas',
            slug='balavikas',
            domain='balavikas.localhost',
            settings={
                'school_name': 'Balavikas',
                'tagline': 'Kannada School',
                'secondary_language': SchoolSettings.SecondaryLanguage.KANNADA,
                'introduction': (
                    'Balavikas is a Kannada learning programme for children living away from Karnataka. '
                    'Students learn to read, write, speak, and enjoy Kannada stories, songs, and culture.'
                ),
                'introduction_secondary': (
                    'ಬಾಲವಿಕಾಸವು ಕರ್ನಾಟಕದಿಂದ ದೂರವಿರುವ ಮಕ್ಕಳಿಗಾಗಿ ಕನ್ನಡ ಕಲಿಕಾ ಕಾರ್ಯಕ್ರಮ. '
                    'ಮಕ್ಕಳು ಕನ್ನಡ ಓದುವುದು, ಬರೆಯುವುದು, ಮಾತನಾಡುವುದು ಮತ್ತು ಕಥೆ-ಹಾಡುಗಳನ್ನು ಕಲಿಯುತ್ತಾರೆ.'
                ),
                'footer_text': 'Balavikas Kannada School',
            },
        )

        self._seed_telugu_course(bmk)
        self._seed_kannada_course(bv)
        self._seed_users(bmk, prefix='bmk')
        self._seed_users(bv, prefix='bv')

        self.stdout.write(self.style.SUCCESS('Seeded schools: balamukundam, balavikas'))

    def _ensure_school(self, name, slug, domain, settings):
        school, _ = School.objects.update_or_create(
            slug=slug,
            defaults={'name': name, 'domain': domain, 'is_active': True},
        )
        SchoolSettings.objects.update_or_create(school=school, defaults=settings)
        return school

    def _seed_users(self, school, prefix):
        password = 'Demo@12345'
        specs = [
            (f'{prefix}_admin', User.Roles.ADMIN, True, True),
            (f'{prefix}_teacher', User.Roles.TEACHER, False, False),
            (f'{prefix}_student', User.Roles.STUDENT, False, False),
        ]
        for username, role, is_staff, is_superuser in specs:
            user, _ = User.objects.update_or_create(
                username=username,
                defaults={
                    'email': f'{username}@{school.slug}.school',
                    'role': role,
                    'school': school,
                    'is_staff': is_staff,
                    'is_superuser': is_superuser,
                    'is_active': True,
                    'email_verified': True,
                    'profile_locked': False,
                },
            )
            user.set_password(password)
            user.save()

    def _seed_telugu_course(self, school):
        course, _ = Course.objects.update_or_create(
            school=school,
            title='Telugu',
            defaults={
                'summary': 'Progressive Telugu levels named after the seven hills of Tirumala.',
                'display_order': 1,
                'display_language': Course.DisplayLanguage.SECONDARY,
                'is_published': True,
                'is_active': True,
            },
        )
        classes = [
            (1, 'Seshadri'),
            (2, 'Garudadri'),
            (3, 'Vrushabhadri'),
            (4, 'Vrushadri'),
            (5, 'Anjanadri'),
            (6, 'Narayanadri'),
            (7, 'Venkatadri'),
        ]
        for order, name in classes:
            defaults = {
                'display_order': order,
                'is_published': True,
                'is_active': True,
                'aim': f'English aims for {name} level.',
                'conditions': 'Attend at least 90% of classes and complete homework on time.',
                'curriculum': f'English curriculum outline for {name}.',
            }
            if name == 'Seshadri':
                defaults.update({
                    'curriculum_secondary': (
                        'చిన్న చిన్న తెలుగు పదాలతో పిల్లలను పూర్తిగా తెలుగులో వాక్యాలు మాట్లాడే విధంగా ఉత్సాహపరచడం\n'
                        'పిల్లలకు అర్థమయ్యేలా ప్రశ్నలడిగి పూర్తివాక్యముగా సమాధానము చెప్పమని అడగడం.\n'
                        'పిల్లలతో, పిల్లలని తెలుగులో మాట్లాడమని, ప్రశ్నలడగమని, సమాధానాలు చెప్పమని సంభాషణ చేయించడం.\n'
                        'అచ్చులు - అక్షరాలని దిద్దించడం.\n'
                        'చిన్న చిన్న పద్యాలు, పాటలు, కథలు నేర్పించడం.'
                    ),
                    'aim_secondary': (
                        'అచ్చులు - వ్రాయడం, చదవడం, గుర్తు పట్టడం.\n'
                        'వారముల పేర్లు నేర్చుకోవడం.\n'
                        'పండ్లు పేర్లు చెప్పడం.\n'
                        '1 నుండి 20 వరకు అంకెలు లెక్కించడం\n'
                        'పద్యాలు, పాటలు అప్పచెప్పడం.'
                    ),
                    'conditions_secondary': (
                        'విద్యార్థులు తప్పని సరిగా 90% తరగతులకు హాజరు కావలెను.\n'
                        'ఇంటిపని(homework)ని నిర్దేశించిన గడువు సమయములో చేయవలెను.\n'
                        'పరీక్షలలో ఉపాధ్యాయులు నిర్ణయించిన లక్ష్యములను సాధించిన విద్యార్థులే ఉన్నత తరగతులకు ఉత్తీర్ణులగుదురు.'
                    ),
                })
            CourseClass.objects.update_or_create(course=course, name=name, defaults=defaults)

    def _seed_kannada_course(self, school):
        course, _ = Course.objects.update_or_create(
            school=school,
            title='Kannada',
            defaults={
                'summary': 'Progressive Kannada learning levels for Balavikas students.',
                'display_order': 1,
                'display_language': Course.DisplayLanguage.SECONDARY,
                'is_published': True,
                'is_active': True,
            },
        )
        classes = [
            (1, 'Level 1', 'Build Kannada alphabet familiarity and simple words.', 'Beginners', 'ಅಕ್ಷರಗಳು, ಸರಳ ಪದಗಳು'),
            (2, 'Level 2', 'Improve reading and speaking confidence.', 'Completed Level 1', 'ಸರಳ ವಾಕ್ಯಗಳು, ಓದು'),
            (3, 'Level 3', 'Develop writing and comprehension.', 'Completed Level 2', 'ಬರವಣಿಗೆ, ಗ್ರಹಿಕೆ'),
            (4, 'Level 4', 'Advance grammar and conversation.', 'Completed Level 3', 'ವ್ಯಾಕರಣ, ಸಂಭಾಷಣೆ'),
        ]
        for order, name, aim, conditions, curriculum_kn in classes:
            CourseClass.objects.update_or_create(
                course=course,
                name=name,
                defaults={
                    'display_order': order,
                    'aim': aim,
                    'conditions': conditions,
                    'curriculum': f'English outline for {name}.',
                    'aim_secondary': aim,
                    'conditions_secondary': conditions,
                    'curriculum_secondary': curriculum_kn,
                    'is_published': True,
                    'is_active': True,
                },
            )
