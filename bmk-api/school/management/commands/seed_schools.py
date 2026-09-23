import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from authentication.usernames import username_for_school_email
from school.models import (
    Course,
    CourseClass,
    SchoolSettings,
    Student,
    Teacher,
)

User = get_user_model()


class Command(BaseCommand):
    help = 'Seed this deployment\'s single school, homepage content, and demo users.'

    @transaction.atomic
    def handle(self, *args, **options):
        slug = os.environ.get('SCHOOL_SLUG', '').strip().lower()
        name = os.environ.get('SCHOOL_NAME', '').strip()
        lesson_app = os.environ.get('SCHOOL_LESSON_APP', '').strip().lower()

        if not slug:
            existing = SchoolSettings.objects.order_by('id').first()
            slug = existing.school_slug if existing else 'uk-telugu'
        if not name:
            existing = SchoolSettings.objects.order_by('id').first()
            name = existing.school_name if existing else slug.replace('-', ' ').title()

        school = self._ensure_school(name=name, slug=slug, lesson_app=lesson_app)

        if slug in {'uk-telugu', 'balamukundam'}:
            self._seed_telugu_course(school)

        prefix = ''.join(ch for ch in slug if ch.isalnum())[:8] or 'sch'
        self._seed_users(school, prefix=prefix)

        self.stdout.write(self.style.SUCCESS(
            f'Seeded singleton school settings for {school.school_name} ({school.school_slug}).'
        ))

    def _settings_for_slug(self, slug, name):
        if slug in {'uk-telugu', 'balamukundam'}:
            return {
                'school_name': 'బాల ముకుందము',
                'tagline': 'తెలుగు పాఠశాల',
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
                    'మాతృదేశానికి ఎంతో దూరంలో ఉన్న మన అందరికి, మన పిల్లలకి, మన మాతృభాష '
                    'నేర్పించాలనే సత్సంకల్పంతో మొదలైనది బాలముకుందం. బాలముకుందంలో మేము '
                    'పిల్లలకి తెలుగు చదవడం, వ్రాయడం, సంభాషించడం మరియు తెలుగు పాటలను, '
                    'పద్యాలను, నీతి కధలను నేర్పడం జరుగుతోంది. పిల్లల వయసు మరియు వారి '
                    'సామర్ధ్యములను దృష్టిలో ఉంచుకొని శేషాద్రి, గరుడాద్రి, వృషభాద్రి, వృషాద్రి, '
                    'అంజనాద్రి, నారయణాద్రి మరియు వెంకటాద్రి తరగతులలో విభజించడం జరిగింది. '
                    'ప్రథమ తరగతైన శేషాద్రిలో చిన్న చిన్న మాటలు, అంకెలు, బొమ్మలు గుర్తించుట, '
                    'బంధుత్వాలు చెప్పడం జరుగుతోంది. క్రమ క్రమంగ తెలుగులో చదవడం, వ్రాయడం '
                    'మరియు వ్యాకరణం నేర్పించడం జరుగుతోంది. ప్రతి ఏడాది పరీక్షలు నిర్వహించడం '
                    'జరుగుతోంది. తెలుగు భాష పై మక్కువ పెరగాలనే ఉద్దేశ్యంతో గ్రంధాలయం ప్రారంభించి, '
                    'తెలుగు కధల పుస్తకములు అందించడం జరుగుతోంది. \n\n'
                    'పిల్లలని ఉత్సాహపరచాలనే ఉద్దేశ్యముతో ప్రతి సంవత్సరం వార్షికోత్సవం జరుపుకోవడం '
                    'జరుగుతోంది. బాలముకుందం శాఖలను ఉచితముగా వివిధ ప్రదేశాలలో ప్రారంభించడం '
                    'కోసము మమ్మలని సంప్రదించండి.'
                ),
                'footer_text': (
                    'బాలముకుందము ఔత్సాహికులయిన ఉపాధ్యాయులు, స్వచ్చందంగా అందిస్తున్న సేవల ఆధారంగా '
                    'నిర్వహింపబడుతున్న ధార్మిక విద్యాసంస్థ. మా పాఠశాలలో పాఠములు, పరీక్షలు, పుస్తకములు '
                    'వంటి బోధనాంశములు అన్ని విద్యార్థులకు ఉచితముగా అందజేయబడును. email:bmtsuk@gmail.com'
                ),
            }
        if slug == 'balavikas':
            return {
                'school_name': 'ಬಾಲವಿಕಾಸ',
                'tagline': 'ಕನ್ನಡ ಪಾಠಶಾಲ',
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
            }
        return {
            'school_name': name,
            'tagline': '',
            'secondary_language': SchoolSettings.SecondaryLanguage.NONE,
            'introduction': f'Welcome to {name}. Classes and schedules are managed by the school team.',
            'introduction_secondary': '',
            'footer_text': name,
        }

    def _ensure_school(self, name, slug, lesson_app=''):
        allowed_apps = {choice for choice, _label in SchoolSettings.LessonApp.choices}
        resolved_app = lesson_app if lesson_app in allowed_apps else SchoolSettings.LessonApp.SIKSHAVAHINI
        if not lesson_app and slug in {'uk-vocalcarnatic', 'uk-flutecarnatic'}:
            resolved_app = SchoolSettings.LessonApp.SUNAADAM

        defaults = self._settings_for_slug(slug, name)
        defaults.update({
            'school_slug': slug,
            'school_number': 1,
            'lesson_app': resolved_app,
        })
        school, _ = SchoolSettings.objects.update_or_create(pk=1, defaults=defaults)
        return school

    def _seed_users(self, school, prefix):
        password = 'Demo@12345'
        specs = [
            (f'{prefix}_admin', User.Roles.ADMIN, True, True),
            (f'{prefix}_teacher', User.Roles.TEACHER, False, False),
            (f'{prefix}_student', User.Roles.STUDENT, False, False),
        ]
        for username, role, is_staff, is_superuser in specs:
            email = f'{username}@{school.school_slug}.school'
            user = User.objects.filter(email__iexact=email).order_by('id').first()
            if user is None:
                user = User(email=email)
            user.username = username if is_superuser else username_for_school_email(email, school)
            user.role = role
            user.is_staff = is_staff
            user.is_superuser = is_superuser
            user.is_active = True
            user.email_verified = True
            user.profile_locked = False
            user.set_password(password)
            user.save()
            if role == User.Roles.STUDENT:
                Student.objects.get_or_create(
                    user=user,
                    defaults={'gender': Student.Gender.BOY},
                )
            elif role == User.Roles.TEACHER:
                Teacher.objects.get_or_create(
                    user=user,
                    defaults={'gender': Teacher.Gender.MALE},
                )

    def _seed_telugu_course(self, school):
        course, _ = Course.objects.update_or_create(
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
            (
                2,
                'Garudadri',
                'హల్లులు - అక్షరాలని దిద్దించడం.\nగుణింతాలు లేని రెండు, మూడు అక్షరముల పదాలను వ్రాయడం, చదవడం.\nపిల్లలచేత చిన్నచిన్న కథలను చెప్పించడము\nచిన్న చిన్న పద్యాలు, పాటలు, కథలు నేర్పించడం.\nసాంస్కృతిక కార్యక్రముములో చిన్న ప్రదర్శన చేయడం.',
                'హల్లులు - వ్రాయడం, చదవడం, గుర్తు పట్టడం.\nఅవయముల పేర్లు నేర్చుకోవడం.\nఅవయములతో, చేసే క్రియలను చెప్పడం. (ఉదాహరణం: కళ్ళతో చూస్తాము)\n1 నుండి 100 వరకు అంకెలులెక్కించడం\nపద్యాలు, పాటలు అప్పచెప్పడం.',
            ),
            (
                3,
                'Vrushabhadri',
                'గుణింతాలు, ఒత్తులు - అక్షరాలని దిద్దించడం\nచిన్న చిన్న పద్యాలు, పాటలు, కథలు నేర్పించడం.\nసాంస్కృతిక కార్యక్రముములో చిన్న ప్రదర్శన చేయడం.',
                'గుణింతాలు, ఒత్తులు - వ్రాయడం, చదవడం, గుర్తు పట్టడం.\nపద్యాలు, పాటలు అప్పచెప్పడం.',
            ),
            (
                4,
                'Vrushadri',
                'పద్యములు, పాఠములు, కథలు పిల్లతో చదివించడం.\nకష్ఠమైన పదములను, వాక్యములను వ్రాయించడం.\nవ్యాకరణము: భాషాభాగములు, లింగములు, వచనములు, విభక్తులు.\nసాంస్కృతిక కార్యక్రముములో చిన్న ప్రదర్శన చేయడం.',
                'తప్పులు లేకుండా తెలుగు వాక్యములను వ్రాయడం.\nపద్యాలు, పాటలు అప్పచెప్పడం.',
            ),
            (
                5,
                'Anjanadri',
                'వివరించి సమధానములు వ్రాయడం.\nసరళ వ్యాసములు, లేఖలు వ్రాయడము.\nచందమామ వంటి పిల్లల పుస్తకములను చదివి వ్యాఖ్యలు చెయ్యడము.\nవ్యాకరణము: సంధులు, సమాసములు\nసాంస్కృతిక కార్యక్రముములో చిన్న ప్రదర్శన చేయడం.',
                'అనర్గళంగా తెలుగులో మాట్లాడటము.\nపద్యములు, కథలు చెప్పటము\nఏదయినా విషయముపై ప్రసంగం చేయడము',
            ),
            (
                6,
                'Narayanadri',
                'వ్యాసములు సంగ్రహముగా వ్రాయడము..\nఅంతర్జాలములో తెలుగు సాహిత్యమును చదివి అర్థము చేసుకోవడము.\nపద్యములకు ప్రతిపదార్థము, భావములు వ్రాయడము.\nవ్యాకరణము: అలంకారములు, చందస్సు.\nసాంస్కృతిక కార్యక్రముములో చిన్న ప్రదర్శన చేయడం.',
                'తెలుగులో చర్చలు, వాదోపవాదాలు చెయ్యడము.\nఆత్మవిశ్వాసముతో సభాముఖముగా మాట్లాడటము.',
            ),
            (
                7,
                'Venkatadri',
                'ఇతరభాషా వ్యాసములను తెలుగులోనికి అనువాదము చెయ్యడము.\nతెలుగులో కవితలు, పాటలు, పద్యాలు స్వంతముగా వ్రాయడము.\nసాంస్కృతిక కార్యక్రముములో చిన్న ప్రదర్శన చేయడం.',
                'తెలుగులో చర్చలు, వాదోపవాదాలు చెయ్యడము.\nఆత్మవిశ్వాసముతో సభాముఖముగా మాట్లాడటము.\nకార్యక్రమములు నిర్వహించడము',
            ),
        ]
        conditions = (
            'విద్యార్థులు తప్పని సరిగా 90% తరగతులకు హాజరు కావలెను.\n'
            'ఇంటిపని(homework)ని నిర్దేశించిన గడువు సమయములో చేయవలెను.\n'
            'పరీక్షలలో ఉపాధ్యాయులు నిర్ణయించిన లక్ష్యములను సాధించిన విద్యార్థులే ఉన్నత తరగతులకు ఉత్తీర్ణులగుదురు.'
        )
        for item in classes:
            order, name = item[:2]
            defaults = {
                'display_order': order,
                'is_published': True,
                'is_active': True,
                'aim': f'English aims for {name} level.',
                'conditions': 'Attend at least 90% of classes and complete homework on time.',
                'curriculum': f'English curriculum outline for {name}.',
            }
            if len(item) == 4:
                _, _, curriculum_secondary, aim_secondary = item
                defaults.update({
                    'curriculum_secondary': curriculum_secondary,
                    'aim_secondary': aim_secondary,
                    'conditions_secondary': conditions,
                })
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

