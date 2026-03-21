from django.db import migrations
from django.db.models import Count
from django.db.models.functions import Lower


INDEX_NAME = 'users_auth_user_email_ci_unique_idx'


def _build_unique_email(User, original_email, user_id):
    local, at_sign, domain = (original_email or '').partition('@')
    if at_sign and local and domain:
        base_local = local
        suffix = f'+dup{user_id}'
        max_local_len = max(1, 254 - len(domain) - 1 - len(suffix))
        trimmed_local = base_local[:max_local_len]
        candidate = f'{trimmed_local}{suffix}@{domain}'
    else:
        candidate = f'duplicate+{user_id}@invalid.local'

    sequence = 1
    while User.objects.filter(email__iexact=candidate).exists():
        sequence += 1
        if at_sign and local and domain:
            suffix = f'+dup{user_id}-{sequence}'
            max_local_len = max(1, 254 - len(domain) - 1 - len(suffix))
            trimmed_local = local[:max_local_len]
            candidate = f'{trimmed_local}{suffix}@{domain}'
        else:
            candidate = f'duplicate+{user_id}-{sequence}@invalid.local'
    return candidate


def normalize_duplicate_emails(apps, schema_editor):
    User = apps.get_model('auth', 'User')

    duplicates = (
        User.objects.exclude(email='')
        .annotate(email_lower=Lower('email'))
        .values('email_lower')
        .annotate(total=Count('id'))
        .filter(total__gt=1)
    )

    for duplicate_group in duplicates:
        email_lower = duplicate_group['email_lower']
        users = list(User.objects.filter(email__iexact=email_lower).order_by('id'))
        # Keep the earliest account's email unchanged; rewrite later duplicates.
        for duplicate_user in users[1:]:
            duplicate_user.email = _build_unique_email(
                User=User,
                original_email=duplicate_user.email,
                user_id=duplicate_user.id,
            )
            duplicate_user.save(update_fields=['email'])


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('users', '0004_userprofile_referral_code_used'),
    ]

    operations = [
        migrations.RunPython(normalize_duplicate_emails, migrations.RunPython.noop),
        migrations.RunSQL(
            sql=(
                f'CREATE UNIQUE INDEX IF NOT EXISTS {INDEX_NAME} '
                'ON auth_user (LOWER(email)) '
                "WHERE email <> ''"
            ),
            reverse_sql=f'DROP INDEX IF EXISTS {INDEX_NAME}',
        ),
    ]
