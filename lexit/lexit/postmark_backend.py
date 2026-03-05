import base64
import json
import logging
from urllib import request, error

from django.conf import settings
from django.core.mail.backends.base import BaseEmailBackend


logger = logging.getLogger(__name__)


class PostmarkBackend(BaseEmailBackend):
    """Django email backend that sends through Postmark's HTTP API."""

    api_url = "https://api.postmarkapp.com/email"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.server_token = getattr(settings, "POSTMARK_SERVER_TOKEN", "")

    def send_messages(self, email_messages):
        if not email_messages:
            return 0

        if not self.server_token:
            logger.error("Postmark server token is not configured")
            return 0

        sent_count = 0
        for message in email_messages:
            if self._send_message(message):
                sent_count += 1
        return sent_count

    def _send_message(self, email_message):
        payload = self._build_payload(email_message)

        req = request.Request(
            self.api_url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
                "X-Postmark-Server-Token": self.server_token,
            },
            method="POST",
        )

        try:
            with request.urlopen(req, timeout=getattr(settings, "EMAIL_TIMEOUT", 30)) as response:
                response_body = response.read().decode("utf-8") if response else ""
                if 200 <= response.status < 300:
                    logger.info("Email sent successfully via Postmark to %s", payload.get("To"))
                    return True

                logger.error("Postmark API error: status=%s body=%s", response.status, response_body)
                return False
        except error.HTTPError as exc:
            body = exc.read().decode("utf-8") if hasattr(exc, "read") else ""
            logger.error("Postmark HTTP error: status=%s body=%s", exc.code, body)
            return False
        except Exception as exc:
            logger.error("Failed to send email via Postmark: %s", str(exc))
            return False

    def _build_payload(self, email_message):
        text_body = email_message.body or ""
        html_body = None

        if getattr(email_message, "alternatives", None):
            for alternative in email_message.alternatives:
                content = getattr(alternative, "content", None)
                mimetype = getattr(alternative, "mimetype", None)

                if content is None and isinstance(alternative, (list, tuple)) and len(alternative) >= 2:
                    content, mimetype = alternative[0], alternative[1]

                if mimetype == "text/html":
                    html_body = content
                    break

        payload = {
            "From": email_message.from_email or settings.DEFAULT_FROM_EMAIL,
            "To": ",".join(email_message.to or []),
            "Subject": email_message.subject or "",
            "TextBody": text_body,
            "MessageStream": "outbound",
        }

        if html_body:
            payload["HtmlBody"] = html_body

        if email_message.cc:
            payload["Cc"] = ",".join(email_message.cc)

        if email_message.bcc:
            payload["Bcc"] = ",".join(email_message.bcc)

        if email_message.reply_to:
            payload["ReplyTo"] = ",".join(email_message.reply_to)

        if getattr(email_message, "attachments", None):
            attachments = []
            for attachment in email_message.attachments:
                if not isinstance(attachment, (list, tuple)) or len(attachment) != 3:
                    continue

                filename, content, mimetype = attachment
                if isinstance(content, str):
                    content_bytes = content.encode("utf-8")
                else:
                    content_bytes = content

                attachments.append(
                    {
                        "Name": filename,
                        "Content": base64.b64encode(content_bytes).decode("utf-8"),
                        "ContentType": mimetype or "application/octet-stream",
                    }
                )

            if attachments:
                payload["Attachments"] = attachments

        return payload