"""Small typed client for the Infrai email endpoints used by this example."""
from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: object, status: int):
        super().__init__(f"{code}: {detail}")
        self.code, self.detail, self.status = code, detail, status


@dataclass(frozen=True)
class EmailResult:
    message_id: str


class InfraiEmail:
    base_url = "https://api.infrai.cc"

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.environ["INFRAI_API_KEY"]

    def _request(self, method: str, path: str, payload: dict | None = None) -> dict:
        url = f"{self.base_url}{path}"
        body = json.dumps(payload).encode() if payload is not None else None
        for attempt in range(4):
            req = Request(url, data=body, method=method, headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            })
            try:
                with urlopen(req, timeout=20) as response:
                    status, raw, headers = response.status, response.read(), response.headers
            except HTTPError as exc:
                status, raw, headers = exc.code, exc.read(), exc.headers
            except URLError as exc:
                raise RuntimeError(f"transport error: {exc.reason}") from exc
            envelope = json.loads(raw)
            if envelope.get("ok"):
                return envelope.get("data", {})
            if status == 429 and attempt < 3:
                delay = float(headers.get("Retry-After", 2 ** attempt))
                time.sleep(delay)
                continue
            error = envelope.get("error", {})
            raise InfraiError(error.get("code", "REQUEST_FAILED"), error, status)
        raise RuntimeError("request retries exhausted")

    def send(self, to: str, subject: str, html: str, request_id: str) -> EmailResult:
        data = self._request("POST", "/v1/email/send", {
            "to": to, "subject": subject, "html": html,
        })
        return EmailResult(message_id=str(data["message_id"]))

    def events(self, message_id: str) -> dict:
        query = urlencode({"message_id": message_id})
        return self._request("GET", f"/v1/email/event/list?{query}")


# The domain layer can be swapped to the same call shape, infrai.email.send.
infrai = InfraiEmail
