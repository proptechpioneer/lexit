import json
import logging
from urllib.parse import quote
from urllib import request as urllib_request, error as urllib_error

from django.conf import settings


logger = logging.getLogger(__name__)


def build_referred_user_identifier(user):
    # Provide a stable, non-contact identifier for referral notifications.
    user_id = getattr(user, "id", None)
    if user_id:
        return f"LXT-{int(user_id):06d}"
    return "LXT-UNKNOWN"


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

        has_referral_token = bool((referral_code or '').strip())

        if contact_id and referral_tag_id and (referred_by or has_referral_token):
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

        if contact_id and has_referral_token:
            normalized_referral_code = _normalize_referral_code(referral_code)
            if normalized_referral_code:
                code_tag_id = _ensure_referral_code_tag(
                    api_url=api_url,
                    api_key=api_key,
                    referral_code=normalized_referral_code,
                )
                if code_tag_id:
                    _post_json(
                        f"{api_url}/api/3/contactTags",
                        {
                            "contactTag": {
                                "contact": str(contact_id),
                                "tag": str(code_tag_id),
                            }
                        },
                        api_key,
                    )
                    applied_tags.append(str(code_tag_id))

        if contact_id and (referred_by or has_referral_token):
            note_lines = [
                "Referral tracked by LEXIT.",
            ]

            if referred_by:
                note_lines.extend([
                    f"Referred by username: {getattr(referred_by, 'username', '')}",
                    f"Referred by email: {getattr(referred_by, 'email', '')}",
                ])
            else:
                note_lines.append("No internal referrer account matched.")

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


def notify_referrer_of_signup(referrer_user, referred_user, referral_code=None):
    """
    Create an ActiveCampaign note for the referrer without exposing the referred user's contact details.
    This can be used to trigger AC automations for referral notifications.
    """
    api_url = (getattr(settings, "ACTIVECAMPAIGN_API_URL", "") or "").strip().rstrip("/")
    api_key = (getattr(settings, "ACTIVECAMPAIGN_API_KEY", "") or "").strip()

    if not api_url or not api_key:
        return {"success": False, "reason": "not_configured"}

    if not getattr(referrer_user, "email", ""):
        return {"success": False, "reason": "missing_referrer_email"}

    try:
        referrer_sync = _post_json(
            f"{api_url}/api/3/contact/sync",
            {
                "contact": {
                    "email": referrer_user.email,
                    "firstName": (getattr(referrer_user, "first_name", "") or "").strip(),
                    "lastName": (getattr(referrer_user, "last_name", "") or "").strip(),
                }
            },
            api_key,
        )

        referrer_contact_id = (
            (referrer_sync.get("contact") or {}).get("id")
            if isinstance(referrer_sync, dict)
            else None
        )
        if not referrer_contact_id:
            return {"success": False, "reason": "missing_referrer_contact_id"}

        referred_identifier = build_referred_user_identifier(referred_user)
        field_update_result = _update_referrer_custom_fields(
            api_url=api_url,
            api_key=api_key,
            contact_id=str(referrer_contact_id),
            referred_identifier=referred_identifier,
            referral_code=referral_code,
        )

        note_lines = [
            "LEXIT referral event.",
            f"You referred a new member: {referred_identifier}",
            "No contact details are included for privacy.",
        ]
        if referral_code:
            note_lines.append(f"Referral token used: {referral_code}")

        _post_json(
            f"{api_url}/api/3/notes",
            {
                "note": {
                    "note": "\n".join(note_lines),
                    "relid": str(referrer_contact_id),
                    "reltype": "Subscriber",
                }
            },
            api_key,
        )

        notification_tag_id = (
            getattr(settings, "ACTIVECAMPAIGN_REFERRER_NOTIFICATION_TAG_ID", "") or ""
        ).strip()
        if notification_tag_id:
            _post_json(
                f"{api_url}/api/3/contactTags",
                {
                    "contactTag": {
                        "contact": str(referrer_contact_id),
                        "tag": str(notification_tag_id),
                    }
                },
                api_key,
            )

        return {
            "success": True,
            "contact_id": str(referrer_contact_id),
            "referred_identifier": referred_identifier,
            "field_updates": field_update_result,
        }
    except Exception as exc:
        logger.warning(
            "ActiveCampaign referrer notification failed for %s: %s",
            getattr(referrer_user, "email", ""),
            str(exc),
        )
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


def _put_json(url, payload, api_key):
    req = urllib_request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Api-Token": api_key,
            "Accept": "application/json",
            "Content-Type": "application/json",
        },
        method="PUT",
    )

    try:
        with urllib_request.urlopen(req, timeout=30) as response:
            body = response.read().decode("utf-8") if response else "{}"
            return json.loads(body) if body else {}
    except urllib_error.HTTPError as exc:
        body = exc.read().decode("utf-8") if hasattr(exc, "read") else ""
        raise RuntimeError(f"HTTP {exc.code}: {body}")


def _get_json(url, api_key):
    req = urllib_request.Request(
        url,
        headers={
            "Api-Token": api_key,
            "Accept": "application/json",
        },
        method="GET",
    )

    try:
        with urllib_request.urlopen(req, timeout=30) as response:
            body = response.read().decode("utf-8") if response else "{}"
            return json.loads(body) if body else {}
    except urllib_error.HTTPError as exc:
        body = exc.read().decode("utf-8") if hasattr(exc, "read") else ""
        raise RuntimeError(f"HTTP {exc.code}: {body}")


def _normalize_referral_code(referral_code):
    return ''.join(ch for ch in (referral_code or '').strip().upper() if ch.isalnum())


def build_referral_code_tag_name(referral_code):
    normalized_referral_code = _normalize_referral_code(referral_code)
    if not normalized_referral_code:
        return ''

    tag_prefix = (
        getattr(settings, "ACTIVECAMPAIGN_REFERRAL_CODE_TAG_PREFIX", "ref=")
        or "ref="
    ).strip()
    return f"{tag_prefix}{normalized_referral_code}"


def _ensure_referral_code_tag(api_url, api_key, referral_code):
    tag_name = build_referral_code_tag_name(referral_code)
    if not tag_name:
        return None

    existing_tag = _find_existing_tag(
        api_url=api_url,
        api_key=api_key,
        tag_name=tag_name,
    )
    if existing_tag:
        return str(existing_tag.get("id"))

    create_response = _post_json(
        f"{api_url}/api/3/tags",
        {
            "tag": {
                "tag": tag_name,
                "tagType": "contact",
                "description": f"Referral code captured at signup: {referral_code}",
            }
        },
        api_key,
    )

    created_tag = (create_response or {}).get("tag") or {}
    created_tag_id = created_tag.get("id")
    return str(created_tag_id) if created_tag_id else None


def _find_existing_tag(api_url, api_key, tag_name):
    encoded_tag_name = quote(tag_name)
    response = _get_json(f"{api_url}/api/3/tags?search={encoded_tag_name}", api_key)
    tags = (response or {}).get("tags") or []

    for tag in tags:
        if str((tag or {}).get("tag", "")).strip().lower() == tag_name.lower():
            return tag
    return None


def _update_referrer_custom_fields(api_url, api_key, contact_id, referred_identifier, referral_code=None):
    updates = []

    configured_fields = [
        (
            getattr(settings, "ACTIVECAMPAIGN_REFERRER_USER_ID_FIELD_NAME", "Latest Referred User ID"),
            referred_identifier,
        ),
        (
            getattr(settings, "ACTIVECAMPAIGN_REFERRER_CODE_FIELD_NAME", "Latest Referral Code Used"),
            referral_code or "",
        ),
    ]

    for field_name, value in configured_fields:
        if not field_name:
            continue

        field = _find_contact_field(api_url=api_url, api_key=api_key, field_name=field_name)
        if not field:
            updates.append({"field_name": field_name, "updated": False, "reason": "field_not_found"})
            continue

        field_id = str(field.get("id") or "")
        if not field_id:
            updates.append({"field_name": field_name, "updated": False, "reason": "missing_field_id"})
            continue

        existing_field_value = _find_existing_field_value(
            api_url=api_url,
            api_key=api_key,
            contact_id=contact_id,
            field_id=field_id,
        )

        payload = {
            "fieldValue": {
                "contact": str(contact_id),
                "field": field_id,
                "value": value,
            }
        }

        if existing_field_value and existing_field_value.get("id"):
            _put_json(
                f"{api_url}/api/3/fieldValues/{existing_field_value['id']}",
                payload,
                api_key,
            )
        else:
            _post_json(
                f"{api_url}/api/3/fieldValues",
                payload,
                api_key,
            )

        updates.append({"field_name": field_name, "updated": True, "value": value})

    return updates


def _find_contact_field(api_url, api_key, field_name):
    normalized_field_name = str(field_name or "").strip().lower()
    if not normalized_field_name:
        return None

    encoded_field_name = quote(field_name)
    response = _get_json(f"{api_url}/api/3/fields?search={encoded_field_name}", api_key)
    fields = (response or {}).get("fields") or []

    for field in fields:
        title = str((field or {}).get("title", "")).strip().lower()
        if title == normalized_field_name:
            return field
    return None


def _find_existing_field_value(api_url, api_key, contact_id, field_id):
    response = _get_json(f"{api_url}/api/3/contacts/{contact_id}/fieldValues", api_key)
    field_values = (response or {}).get("fieldValues") or []

    for field_value in field_values:
        if str((field_value or {}).get("field", "")) == str(field_id):
            return field_value
    return None
