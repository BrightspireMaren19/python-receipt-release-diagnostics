from decimal import Decimal

from receipt_service import EmailResult, InfraiEmail, Order, release_receipt


class FakeEmail(InfraiEmail):
    def __init__(self):
        pass

    def send(self, to, subject, html, request_id):
        assert to == "dev@example.com"
        assert "ord-7" in subject
        assert "19.50" in html
        assert request_id == "release:ord-7"
        return EmailResult("msg-7")

    def events(self, message_id):
        assert message_id == "msg-7"
        return {"events": [{"type": "delivered"}]}


def test_release_models_build_release_and_delivery_diagnostic():
    report = release_receipt(Order("ord-7", "dev@example.com", Decimal("19.50")), FakeEmail())
    assert report.build_event == "build:ord-7:receipt"
    assert report.release_operation == "release:ord-7"
    assert report.diagnostics == "message msg-7; events=1"
