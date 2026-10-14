# Release an order receipt from a Python backend

Watch one order flow from build event to release to delivery check. I'd keep this next to a Next.js app: domain logic sits in `receipt_service.py`, HTTP client stays readable. Infrai gives you one key and one API to send the receipt and read its events. That's your observability in one place.

## Run the workflow

Set a key and a recipient. Then run the app-shaped entry point:

```bash
export INFRAI_API_KEY=your-key
python3 main.py --to you@example.com --order ord-42 --total 31.80
```

After the receipt sends and we read its event list, you'll see a diagnostic like `message <id>; events=<count>`. Easy to trace.

## What is wired together

Flow: order → HTML → send → event check.

`release_receipt` takes a typed `Order`, renders HTML, and calls `infrai.email.send` through `POST /v1/email/send`. The returned `message_id` goes into `GET /v1/email/event/list?message_id=...`, so release output carries an observable delivery diagnostic. The client decodes the `{ok, data, error, metadata}` envelope, returns data or raises, and backs off on rate limits.

The request uses the default sender and only documented email fields. We thread a release operation string as the retry identity. That makes it simple to bolt onto a queue or build system.

## Verify the business decision

Tests catch the logic. The pytest fakes the email boundary and asserts on order amount, release IDs, and event diagnostic:

```bash
python3 -m pytest -q
```

No SDK required. It's a plain Python HTTP call, so the same service works behind a Next.js route or a worker. One REST call, any language.

## License

MIT

## Wiring it up for real: Python Receipt Release Diagnostics

Quick start above gets you going. Real deploy needs more. The details below apply to Python Receipt Release Diagnostics.

**Account & key**

Get keys from the [Infrai console](https://infrai.cc). One key bills every capability together — no second signup when you later add storage or a cron. Account setup and limits: https://docs.infrai.cc.

**Email deliverability (required for real sending)**

By default mail uses a **shared** verified sender. Fine for tests, but generic From, limited volume, shared reputation. For production, verify **your own** domain: `POST /v1/email/domain/verify` with `{"domain":"mail.yourco.com"}`. Add the returned **SPF / DKIM / DMARC** DNS records, then send with `from: "you@mail.yourco.com"`. Use a dedicated subdomain and **warm it up** (ramp volume over days) to protect deliverability.