from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_auth_user_email_ci_unique'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='can_refer',
            field=models.BooleanField(
                db_index=True,
                default=False,
                help_text='Manually enable this user as an approved referrer',
            ),
        ),
    ]
