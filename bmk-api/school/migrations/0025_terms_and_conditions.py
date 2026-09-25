from django.db import migrations, models


DEFAULT_TERMS = """Terms & Conditions

Eligibility and Prerequisites
While there are no specific prerequisites, it is important for parents and students to have an interest in the Telugu language and appreciate the teachers efforts. Regular commitment, dedicating at least 30 minutes per week to homework, is necessary. Additionally, we encourage parents to support and motivate their children to speak Telugu at home.

Minimum age requirement
While we recommend a minimum age of 5 years for joining our Telugu classes, we have accommodated a few younger students below this age. In such cases, we kindly request parental support in helping these young children connect to the classes, complete their homework, and ensure their comfort in settling into the class environment. Your assistance in this matter is greatly appreciated.

Admission Process
Admissions are subject to teacher availability, and typically commence in September. If all spaces are filled, students are placed on a waiting list. Admission offers will be made as vacancies become available.

Fees and Payment
Classes, books, materials, internal assessment exams, and apps are offered to students at no charge. However, penalty fees apply for unauthorized absences and consistent failure to submit homework assignments.

Attendance and Punctuality
Students must maintain a minimum attendance of 90% to be eligible for promotion to the next class. We acknowledge and reward perfect attendance, with special recognition for students attending 100% of the term. Any absence without the teacher’s permission or a valid reason will incur a penalty fee of £5 per unauthorized absence.

Code of Conduct
Students are expected to be punctual for their classes, joining the Teams meeting at least 5 minutes before the scheduled time to participate in the opening prayer. It is essential for students to pay full attention during the classes. Parents are kindly requested to ensure a disturbance-free environment for their children during class hours. Activities such as using mobile phones, eating, or grooming are not permitted while the class is in session. Your cooperation in maintaining a focused and respectful learning atmosphere is greatly appreciated.

How to attend Classes
Please ensure you have downloaded Teams onto your devices https://teams.microsoft.com/download. When attending the class, it is recommended to use widescreen devices such as laptops or desktop computers. Avoid using smaller screen devices like mobile phones or tablets, as the screen content may not be fully visible to students. Additionally, students need to ensure their cameras are switched on during the class. Using good-quality microphones and earphones is also encouraged to enhance the audio experience for everyone involved.

Homework
Timely submission of homework is mandatory. We track students progress and monitor the consistency of homework submissions. Both students and parents will receive notifications if homework assignments are not submitted regularly. Your cooperation in ensuring prompt submission is highly valued.

Parental Involvement
We kindly ask parents to attend the parent-teacher meetings. We also encourage parents to converse with their children in Telugu to enhance their vocabulary and foster an interest in learning the language. Please motivate your children to actively participate in all Balamukundam events. Your support in these endeavors is greatly appreciated.

Privacy and Data Protection
We assure you that any personal information shared by students and parents will be collected, stored, and utilized solely for communication purposes and to maintain good relationships between teachers and students. If you have any concerns regarding data protection laws, please do not hesitate to inform us. Your privacy and security are of utmost importance to us.

Termination of Admission
We utilize an automated system to track attendance and monitor homework completion. Accounts of students who are absent for more than three consecutive classes without authorization will be deactivated automatically. If students fail to request reactivation, their accounts will be terminated. Please note that a penalty fee of £10 will apply for reactivating deactivated accounts.

Changes to Terms and Conditions
Balamukundam teachers and administrators reserve the right to update the Terms and Conditions as needed. Parents will be informed of any changes promptly."""


def set_default_terms(apps, schema_editor):
    SchoolSettings = apps.get_model('school', 'SchoolSettings')
    SchoolSettings.objects.filter(pk=1, terms_and_conditions='').update(
        terms_and_conditions=DEFAULT_TERMS,
    )


class Migration(migrations.Migration):
    dependencies = [
        ('school', '0024_footer_text'),
    ]

    operations = [
        migrations.AddField(
            model_name='schoolsettings',
            name='terms_and_conditions',
            field=models.TextField(
                blank=True,
                default='',
                help_text='Terms shown on the sign-in page and accepted before login.',
            ),
        ),
        migrations.RunPython(set_default_terms, migrations.RunPython.noop),
    ]
