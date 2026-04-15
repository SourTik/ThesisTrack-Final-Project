from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='category',
            field=models.CharField(
                choices=[
                    ('APPROVAL', 'Approval'),
                    ('FEEDBACK', 'Feedback'),
                    ('DEADLINE', 'Deadline'),
                    ('GENERAL', 'General'),
                ],
                default='GENERAL',
                max_length=20,
            ),
        ),
    ]
