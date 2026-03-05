import json
import logging
from urllib import request as urllib_request, error as urllib_error

from django.conf import settings


logger = logging.getLogger(__name__)


def sync_contact(user, referral_code=None, referred_by=None):
    api_url = (getattr(settings, "ACTIVECAMPAIGN_API_URL", "") or "").strip().rstrip("/")
    api_key = (getattr(settings, "ACTIVECAMPAIGN_API_KEY", "") or "").strip()

    if not api_url or not api_key:
        return {"success": False, "reason": "not_configured"}

    if not getattr(user, "email", ""):
        return {"success": False, "reason": "missing_email"}

    contact_payload = {
        "contact": {
            "email": user.email,
            "firstName": (getattr(user, "first_name", "") or "").strip(),
            "lastName": (getattr(user, "last_name", "") or "").strip(),
        }
    }

    try:
        sync_response = _post_json(
            f"{api_url}/api/3/contact/sync",
            contact_payload,
            api_key,
        )

        contact_id = (
            (sync_response.get("contact") or {}).get("id")
            if isinstance(sync_response, dict)
            else None
        )

        list_id = (getattr(settings, "ACTIVECAMPAIGN_DEFAULT_LIST_ID", "") or "").strip()
        if list_id and contact_id:
            _post_json(
                f"{api_url}/api/3/contactLists",
                {
                    "contactList": {
                        "list": str(list_id),
                        "contact": str(contact_id),
                        "status": 1,
                    }
                },
                api_key,
            )

        applied_tags = []
        signup_tag_id = (getattr(settings, "ACTIVECAMPAIGN_SIGNUP_TAG_ID", "") or "").strip()
        referral_tag_id = (getattr(settings, "ACTIVECAMPAIGN_REFERRAL_TAG_ID", "") or "").strip()

        if contact_id and signup_tag_id:
            _post_json(
                f"{api_url}/api/3/contactTags",
                {
                    "contactTag": {
                        "contact": str(contact_id),
                        "tag": str(signup_tag_id),
                    }
                },
                api_key,
            )
            applied_tags.append(str(signup_tag_id))

        if contact_id and referral_tag_id and referred_by:
            _post_json(
                f"{api_url}/api/3/contactTags",
                {
                    "contactTag": {
                        "contact": str(contact_id),
                        "tag": str(referral_tag_id),
                    }
                },
                api_key,
            )
            applied_tags.append(str(referral_tag_id))

        if contact_id and referred_by:
            note_lines = [
                "Referral tracked by LEXIT.",
                f"Referred by username: {getattr(referred_by, 'username', '')}",
                f"Referred by email: {getattr(referred_by, 'email', '')}",
            ]
            if referral_code:
                note_lines.append(f"Referral code used: {referral_code}")

            _post_json(
                f"{api_url}/api/3/notes",
                {
                    "note": {
                        "note": "\n".join(note_lines),
                        "relid": str(contact_id),
                        "reltype": "Subscriber",
                    }
                },
                api_key,
            )

        return {"success": True, "contact_id": contact_id, "applied_tags": applied_tags}
    except Exception as exc:
        logger.warning("ActiveCampaign sync failed for %s: %s", user.email, str(exc))
        return {"success": False, "reason": str(exc)}


def _post_json(url, payload, api_key):
    req = urllib_request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Api-Token": api_key,
            "Accept": "application/json",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib_request.urlopen(req, timeout=30) as response:
            body = response.read().decode("utf-8") if response else "{}"
            return json.loads(body) if body else {}
    except urllib_error.HTTPError as exc:
        body = exc.read().decode("utf-8") if hasattr(exc, "read") else ""
        raise RuntimeError(f"HTTP {exc.code}: {body}")
