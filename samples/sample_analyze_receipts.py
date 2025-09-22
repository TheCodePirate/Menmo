"""Analyze receipts with the Document Intelligence prebuilt model."""
from __future__ import annotations

import argparse
from typing import Optional

from azure.ai.documentintelligence.models import AnalyzedDocument, DocumentField

from _helpers import (
    add_common_arguments,
    analyze_document,
    create_client,
    value_with_confidence,
)

MODEL_ID = "prebuilt-receipt"


def print_field(label: str, field: Optional[DocumentField], indent: int = 4) -> None:
    value, confidence = value_with_confidence(field)
    prefix = " " * indent + f"{label}: "
    if value is None or value == "":
        print(prefix + "--")
        return
    text = value
    if confidence:
        text += f" (confidence: {confidence})"
    print(prefix + text)


def print_line_items(items_field: Optional[DocumentField]) -> None:
    if items_field is None or not items_field.value_array:
        print("    Line items: --")
        return
    print("    Line items:")
    for index, item in enumerate(items_field.value_array, start=1):
        details = item.value_object or {}
        description, desc_conf = value_with_confidence(details.get("Description"))
        header = f"      {index}. {description or 'Item'}"
        if desc_conf:
            header += f" (confidence: {desc_conf})"
        print(header)
        quantity, qty_conf = value_with_confidence(details.get("Quantity"))
        if quantity:
            line = f"         Quantity: {quantity}"
            if qty_conf:
                line += f" (confidence: {qty_conf})"
            print(line)
        price, price_conf = value_with_confidence(details.get("Price"))
        if price:
            line = f"         Price: {price}"
            if price_conf:
                line += f" (confidence: {price_conf})"
            print(line)
        total, total_conf = value_with_confidence(details.get("TotalPrice"))
        if total:
            line = f"         Line total: {total}"
            if total_conf:
                line += f" (confidence: {total_conf})"
            print(line)
        category, category_conf = value_with_confidence(details.get("Category"))
        if category:
            line = f"         Category: {category}"
            if category_conf:
                line += f" (confidence: {category_conf})"
            print(line)
        sku, sku_conf = value_with_confidence(details.get("ProductCode"))
        if sku:
            line = f"         Product code: {sku}"
            if sku_conf:
                line += f" (confidence: {sku_conf})"
            print(line)


def describe_receipt(receipt: AnalyzedDocument, index: int) -> None:
    print(f"-------- Receipt #{index} ({receipt.doc_type or 'receipt'}) --------")
    fields = receipt.fields or {}
    print("  Merchant details")
    print_field("Name", fields.get("MerchantName"))
    print_field("Address", fields.get("MerchantAddress"))
    print_field("Phone", fields.get("MerchantPhoneNumber"))
    print_field("Email", fields.get("MerchantEmail"))
    print_field("Website", fields.get("MerchantWebsite"))
    print("  Purchase information")
    print_field("Receipt type", fields.get("ReceiptType"))
    print_field("Transaction date", fields.get("TransactionDate"))
    print_field("Transaction time", fields.get("TransactionTime"))
    print_field("Transaction ID", fields.get("TransactionId"))
    print_field("Payment method", fields.get("PaymentMethod"))
    print_field("Tip suggestion", fields.get("TipSuggestions"))
    print_line_items(fields.get("Items"))
    print("  Totals")
    print_field("Subtotal", fields.get("Subtotal"))
    print_field("Tax", fields.get("TotalTax"))
    print_field("Tip", fields.get("Tip"))
    print_field("Total", fields.get("Total"))


def main() -> None:
    parser = add_common_arguments(argparse.ArgumentParser(description="Analyze retail receipts."))
    args = parser.parse_args()

    client = create_client(args.endpoint, args.key)
    result = analyze_document(
        client,
        MODEL_ID,
        args.document,
        locale=args.locale,
        pages=args.pages,
    )

    documents = getattr(result, "documents", [])
    if not documents:
        print("No receipt documents were returned.")
        return

    for index, receipt in enumerate(documents, start=1):
        describe_receipt(receipt, index)


if __name__ == "__main__":
    main()
