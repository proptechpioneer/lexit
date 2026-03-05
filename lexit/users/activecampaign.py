import json
import logging
from urllib import request as urllib_request, error as urllib_error

from django.conf import settings


logger = logging.getLogger(__name__)


def sync_contact(user):
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

        return {"success": True, "contact_id": contact_id}
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
