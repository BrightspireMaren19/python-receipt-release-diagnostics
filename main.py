import argparse
from decimal import Decimal

from infrai_client import InfraiEmail
from receipt_service import Order, release_receipt


def main() -> None:
    parser = argparse.ArgumentParser(description="Release an order receipt email")
    parser.add_argument("--to", required=True, help="customer email address")
    parser.add_argument("--order", default="demo-1001")
    parser.add_argument("--total", default="24.90")
    args = parser.parse_args()
    report = release_receipt(
        Order(args.order, args.to, Decimal(args.total)), InfraiEmail()
    )
    print(report.diagnostics)


if __name__ == "__main__":
    main()
