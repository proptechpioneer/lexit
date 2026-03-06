from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_userprofile_referral_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='referral_code_used',
            field=models.CharField(
                blank=True,
                db_index=True,
                help_text='Original referral token submitted at signup for audit and CRM tagging',
                max_length=64,
                null=True,
            ),
        ),
    ]
