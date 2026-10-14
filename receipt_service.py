from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from infrai_client import EmailResult, InfraiEmail


@dataclass(frozen=True)
class Order:
    order_id: str
    customer_email: str
    total: Decimal
    currency: str = "USD"


@dataclass(frozen=True)
class ReleaseReport:
    build_event: str
    release_operation: str
    diagnostics: str
    email: EmailResult


def render_receipt(order: Order) -> str:
    return (
        f"<h1>Receipt for order {order.order_id}</h1>"
        f"<p>Total: {order.currency} {order.total:.2f}</p>"
    )


def release_receipt(order: Order, client: InfraiEmail) -> ReleaseReport:
    """Model a build event, release operation, then inspect the delivered message."""
    build_event = f"build:{order.order_id}:receipt"
    release_operation = f"release:{order.order_id}"
    email = client.send(
        order.customer_email,
        f"Receipt for order {order.order_id}",
        render_receipt(order),
        request_id=release_operation,
    )
    events = client.events(email.message_id)
    diagnostics = f"message {email.message_id}; events={len(events.get('events', []))}"
    return ReleaseReport(build_event, release_operation, diagnostics, email)
