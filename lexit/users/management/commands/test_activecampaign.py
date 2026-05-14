from datetime import datetime, timezone
from types import SimpleNamespace

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from users.activecampaign import notify_referrer_of_signup, sync_contact


class Command(BaseCommand):
    help = (
        "Run a live ActiveCampaign integration health check by syncing a disposable "
        "contact and optionally triggering a referrer-notification event."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--email",
            type=str,
            default="",
            help="Disposable email for sync test. Defaults to ac.health.<timestamp>@example.com",
        )
        parser.add_argument(
            "--ref-code",
            type=str,
            default="ACHEALTH01",
            help="Referral code to test referral tagging behavior.",
        )
        parser.add_argument(
            "--skip-referrer-notification",
            action="store_true",
            help="Skip the notify_referrer_of_signup check.",
        )

    def handle(self, *args, **options):
        api_url = (getattr(settings, "ACTIVECAMPAIGN_API_URL", "") or "").strip()
        api_key = (getattr(settings, "ACTIVECAMPAIGN_API_KEY", "") or "").strip()

        if not api_url or not api_key:
            raise CommandError(
                "ActiveCampaign is not configured. Set ACTIVECAMPAIGN_API_URL and "
                "ACTIVECAMPAIGN_API_KEY first."
            )

        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        email = (options.get("email") or "").strip() or f"ac.health.{timestamp}@example.com"
        referral_code = (options.get("ref_code") or "").strip()

        self.stdout.write(self.style.NOTICE("Running ActiveCampaign sync health check..."))
        self.stdout.write(f"API URL: {api_url}")
        self.stdout.write(f"Test Email: {email}")
        if referral_code:
            self.stdout.write(f"Referral Code: {referral_code}")

        sync_user = SimpleNamespace(
            email=email,
            first_name="AC",
            last_name="HealthCheck",
        )

        sync_result = sync_contact(sync_user, referral_code=referral_code)
        self.stdout.write(f"sync_contact result: {sync_result}")

        if not sync_result.get("success"):
            raise CommandError(
                f"sync_contact failed: {sync_result.get('reason') or 'unknown error'}"
            )

        if options.get("skip_referrer_notification"):
            self.stdout.write(self.style.SUCCESS("ActiveCampaign sync check passed."))
            return

        self.stdout.write(self.style.NOTICE("Running referrer notification health check..."))

        referrer_user = SimpleNamespace(
            email=f"ac.referrer.{timestamp}@example.com",
            first_name="AC",
            last_name="Referrer",
        )
        referred_user = SimpleNamespace(
            id=999999,
            email=email,
        )

        notify_result = notify_referrer_of_signup(
            referrer_user=referrer_user,
            referred_user=referred_user,
            referral_code=referral_code,
        )
        self.stdout.write(f"notify_referrer_of_signup result: {notify_result}")

        if not notify_result.get("success"):
            raise CommandError(
                "Referrer notification check failed: "
                f"{notify_result.get('reason') or 'unknown error'}"
            )

        self.stdout.write(self.style.SUCCESS("ActiveCampaign integration checks passed."))