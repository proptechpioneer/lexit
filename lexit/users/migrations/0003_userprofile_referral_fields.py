from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import secrets
import string


def _generate_code(existing_codes, length=8):
    alphabet = string.ascii_uppercase + string.digits
    candidate = ''.join(secrets.choice(alphabet) for _ in range(length))
    while candidate in existing_codes:
        candidate = ''.join(secrets.choice(alphabet) for _ in range(length))
    return candidate


def populate_referral_codes(apps, schema_editor):
    UserProfile = apps.get_model('users', 'UserProfile')
    existing_codes = set(
        UserProfile.objects.exclude(referral_code__isnull=True)
        .exclude(referral_code='')
        .values_list('referral_code', flat=True)
    )

    for profile in UserProfile.objects.all().only('id', 'referral_code'):
        if not profile.referral_code:
            profile.referral_code = _generate_code(existing_codes)
            existing_codes.add(profile.referral_code)
            profile.save(update_fields=['referral_code'])


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_honeypotattempt_securityevent'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='referral_code',
            field=models.CharField(
                blank=True,
                db_index=True,
                help_text='Unique referral code used in signup links',
                max_length=12,
                null=True,
                unique=True,
            ),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='referred_at',
            field=models.DateTimeField(
                blank=True,
                help_text='When the referral was attributed',
                null=True,
            ),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='referred_by',
            field=models.ForeignKey(
                blank=True,
                help_text='User who referred this account',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='referred_users',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.RunPython(populate_referral_codes, migrations.RunPython.noop),
    ]
