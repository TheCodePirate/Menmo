"""Analyze invoices with the Document Intelligence prebuilt model."""
from __future__ import annotations

import argparse
from typing import Callable, Optional

from azure.ai.documentintelligence.models import AnalyzedDocument, DocumentField

from _helpers import (
    add_common_arguments,
    analyze_document,
    create_client,
    value_with_confidence,
)

MODEL_ID = "prebuilt-invoice"


def print_field(
    label: str,
    field: Optional[DocumentField],
    indent: int = 4,
    formatter: Optional[Callable[[DocumentField], str]] = None,
) -> None:
    value, confidence = value_with_confidence(field, formatter=formatter)
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
        item_details = item.value_object or {}
        description, desc_conf = value_with_confidence(item_details.get("Description"))
        header = f"      {index}. {description or 'Item'}"
        if desc_conf:
            header += f" (confidence: {desc_conf})"
        print(header)
        quantity, qty_conf = value_with_confidence(item_details.get("Quantity"))
        if quantity:
            line = f"         Quantity: {quantity}"
            if qty_conf:
                line += f" (confidence: {qty_conf})"
            print(line)
        unit, unit_conf = value_with_confidence(item_details.get("Unit"))
        if unit:
            line = f"         Unit: {unit}"
            if unit_conf:
                line += f" (confidence: {unit_conf})"
            print(line)
        unit_price, unit_price_conf = value_with_confidence(item_details.get("UnitPrice"))
        if unit_price:
            line = f"         Unit price: {unit_price}"
            if unit_price_conf:
                line += f" (confidence: {unit_price_conf})"
            print(line)
        amount, amount_conf = value_with_confidence(item_details.get("Amount"))
        if amount:
            line = f"         Line total: {amount}"
            if amount_conf:
                line += f" (confidence: {amount_conf})"
            print(line)
        tax, tax_conf = value_with_confidence(item_details.get("Tax"))
        if tax:
            line = f"         Tax: {tax}"
            if tax_conf:
                line += f" (confidence: {tax_conf})"
            print(line)
        product_code, product_conf = value_with_confidence(item_details.get("ProductCode"))
        if product_code:
            line = f"         Product code: {product_code}"
            if product_conf:
                line += f" (confidence: {product_conf})"
            print(line)
        item_date, item_date_conf = value_with_confidence(item_details.get("Date"))
        if item_date:
            line = f"         Date: {item_date}"
            if item_date_conf:
                line += f" (confidence: {item_date_conf})"
            print(line)


def describe_invoice(invoice: AnalyzedDocument, index: int) -> None:
    print(f"-------- Invoice #{index} ({invoice.doc_type or 'invoice'}) --------")
    fields = invoice.fields or {}
    print("  Vendor details")
    print_field("Name", fields.get("VendorName"))
    print_field("Address", fields.get("VendorAddress"))
    print_field("Recipient", fields.get("VendorAddressRecipient"))
    print_field("Tax ID", fields.get("VendorTaxId"))
    print_field("Phone", fields.get("VendorPhoneNumber"))
    print_field("Email", fields.get("VendorEmail"))
    print("  Customer details")
    print_field("Name", fields.get("CustomerName"))
    print_field("ID", fields.get("CustomerId"))
    print_field("Address", fields.get("CustomerAddress"))
    print_field("Recipient", fields.get("CustomerAddressRecipient"))
    print_field("Tax ID", fields.get("CustomerTaxId"))
    print_field("Billing address", fields.get("BillingAddress"))
    print_field("Billing recipient", fields.get("BillingAddressRecipient"))
    print_field("Shipping address", fields.get("ShippingAddress"))
    print_field("Shipping recipient", fields.get("ShippingAddressRecipient"))
    print("  Invoice info")
    print_field("Invoice ID", fields.get("InvoiceId"))
    print_field("Invoice date", fields.get("InvoiceDate"))
    print_field("Due date", fields.get("DueDate"))
    print_field("Purchase order", fields.get("PurchaseOrder"))
    print_field("Service period start", fields.get("ServiceStartDate"))
    print_field("Service period end", fields.get("ServiceEndDate"))
    print_field("Service address", fields.get("ServiceAddress"))
    print_field("Service recipient", fields.get("ServiceAddressRecipient"))
    print_line_items(fields.get("Items"))
    print("  Totals")
    print_field("Subtotal", fields.get("SubTotal"))
    print_field("Tax", fields.get("TotalTax"))
    print_field("Previous balance", fields.get("PreviousUnpaidBalance"))
    print_field("Amount due", fields.get("AmountDue"))
    print_field("Invoice total", fields.get("InvoiceTotal"))


def main() -> None:
    parser = add_common_arguments(argparse.ArgumentParser(description="Analyze invoice documents."))
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
        print("No invoice documents were returned.")
        return

    for position, invoice in enumerate(documents, start=1):
        describe_invoice(invoice, position)


if __name__ == "__main__":
    main()
