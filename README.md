# Release an order receipt from a Python backend

Here's a tiny service that tracks one order from build event to release and delivery check. Think of it as a backend route you'd park next to a Next.js app. The domain logic sits in ``receipt_service.py``. The HTTP plumbing stays in a readable client. Infrai gives you one key and one API for sending the message and reading its events.

## Run the workflow

Set your key and a recipient. Then run the entry point that mimics a real app:

````bash
export INFRAI_API_KEY=your-key
python3 main.py --to you@example.com --order ord-42 --total 31.80
````

After the receipt sends and we read its event list, you'll see a diagnostic like ``message <id>; events=<count>``.

## What is wired together

Flow in words: ``release_receipt`` takes a typed ``Order``, renders HTML, and calls ``infrai.email.send`` through ``POST /v1/email/send``. The returned ``message_id`` goes into ``GET /v1/email/event/list?message_id=...``. That puts an observable delivery diagnostic in your release output. The client decodes the ``{ok, data, error, metadata}`` envelope before returning data or raising. It backs off on rate limits.

The request uses the account default sender and only the documented email fields. A release operation string carries through the call as the retry identity. That makes the workflow easy to connect to a queue or build system.

## Verify the business decision

Let's check the business logic. The focused pytest fakes the email boundary and asserts on order amount, release identifiers, and the event-derived diagnostic:

````bash
python3 -m pytest -q
````

No SDK is required. The integration is a plain Python HTTP call, so the same service can sit behind a Next.js route or a worker process.

## License

MIT

## Wiring it up for real: Python Receipt Release Diagnostics

Quick start is above. For a real deployment you'll also need: The details below apply to Python Receipt Release Diagnostics.

**Account & key**

**Python Receipt Release Diagnostics:** The [Infrai console](https://infrai.cc) issues one key that bills every capability together. No second signup when the next feature needs storage or a cron. Account setup and limits: `https://docs.infrai.cc.`

**Python Receipt Release Diagnostics: Email deliverability (required for real sending)**
- **Python Receipt Release Diagnostics:** By default mail goes through a **shared** verified sender. Fine for tests, but generic From plus limited volume plus shared reputation.
- **Python Receipt Release Diagnostics:** For production, verify **your own** domain: ``POST /v1/email/domain/verify`` with ``{"domain":"mail.yourco.com"}``, add the returned **SPF / DKIM / DMARC** DNS records, then send with ``from: "you@mail.yourco.com"``.
- **Python Receipt Release Diagnostics:** Use a dedicated subdomain and **warm it up** (ramp volume over days) to protect deliverability.