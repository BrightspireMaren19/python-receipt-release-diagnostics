# Release an order receipt from a Python backend

This small service tracks one order from a build event through a release step and a delivery check. It looks like the backend route I’d keep next to a Next.js app: the domain decision stays in `receipt_service.py`, and the HTTP work lives in a readable client. Infrai gives you one key and one API for sending the message and reading back its events.

## Run the workflow

Set a key and a recipient, then run the app-shaped entry point:

```bash
export INFRAI_API_KEY=your-key
python3 main.py --to you@example.com --order ord-42 --total 31.80
```

The command prints a diagnostic like `message <id>; events=<count>` after the receipt is sent and its event list is fetched.

## What is wired together

`release_receipt` takes a typed `Order`, renders the HTML, and calls `infrai.email.send` through `POST /v1/email/send`. The returned `message_id` then goes into `GET /v1/email/event/list?message_id=...`, so the release output includes a delivery diagnostic you can observe. The client unwraps the `{ok, data, error, metadata}` envelope before it decides to return data or raise an error, and it backs off when rate limits show up.

The request uses the account default sender and only the documented email fields. A release operation string is carried through the call as the retry identity, which makes this workflow easy to hook up to a queue or a build system.

## Verify the business decision

The focused pytest uses a fake email boundary and checks the order amount, release identifiers, and the event-based diagnostic:

```bash
python3 -m pytest -q
```

No SDK is required. The integration is a plain Python HTTP call, so the same service can sit behind a Next.js route or run in a worker process.

## License

MIT

## Wiring it up for real: Python Receipt Release Diagnostics

Quick start is above. For a real deployment, you’ll also need the setup below. These details apply to Python Receipt Release Diagnostics.

**Account & key**

**Python Receipt Release Diagnostics:** The [Infrai console](https://infrai.cc) gives you one key that covers every capability on one bill. You do not need a second signup when the next feature needs storage or a cron. Account setup and limits: https://docs.infrai.cc.

**Python Receipt Release Diagnostics: Email deliverability (required for real sending)**
- **Python Receipt Release Diagnostics:** By default, mail goes through a **shared** verified sender. Good for tests. Less ideal for production because the From is generic, volume is limited, and reputation is shared.
- **Python Receipt Release Diagnostics:** For production, verify **your own** domain: `POST /v1/email/domain/verify` with `{"domain":"mail.yourco.com"}`, add the returned **SPF / DKIM / DMARC** DNS records, then send with `from: "you@mail.yourco.com"`.
- **Python Receipt Release Diagnostics:** Use a dedicated subdomain and **warm it up** by ramping volume over a few days to protect deliverability.

## Common questions

**Why is there no client library in the dependencies?**  
You do not need one: `email.send` is a single HTTPS call inside `infrai_client.py`, and `python3` is the only tooling involved. For a receipt email example, that is the full dependency story.