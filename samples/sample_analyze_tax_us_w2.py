"""Analyze US W-2 tax forms with the Document Intelligence prebuilt model."""
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

MODEL_ID = "prebuilt-tax.us.w2"


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


def describe_party(label: str, party_field: Optional[DocumentField]) -> None:
    print(f"  {label}")
    if party_field is None or not party_field.value_object:
        print("    --")
        return
    details = party_field.value_object
    print_field("Name", details.get("Name"))
    id_field = details.get("IdNumber")
    if id_field is not None:
        print_field("ID", id_field)
    ssn_field = details.get("SocialSecurityNumber")
    if ssn_field is not None:
        print_field("SSN", ssn_field)
    print_field("Address", details.get("Address"))


def describe_additional_info(additional_field: Optional[DocumentField]) -> None:
    print("  Additional information")
    if additional_field is None or not additional_field.value_array:
        print("    --")
        return
    for entry in additional_field.value_array:
        data = entry.value_object or {}
        letter, letter_conf = value_with_confidence(data.get("LetterCode"))
        amount, amount_conf = value_with_confidence(data.get("Amount"))
        parts = []
        if letter:
            part = f"Code {letter}"
            if letter_conf:
                part += f" (confidence: {letter_conf})"
            parts.append(part)
        if amount:
            part = f"Amount {amount}"
            if amount_conf:
                part += f" (confidence: {amount_conf})"
            parts.append(part)
        if parts:
            print("    - " + "; ".join(parts))


def describe_w2(document: AnalyzedDocument, index: int) -> None:
    print(f"-------- W-2 #{index} ({document.doc_type or 'tax.us.w2'}) --------")
    fields = document.fields or {}
    print_field("Form variant", fields.get("W2FormVariant"))
    print_field("Tax year", fields.get("TaxYear"))
    print_field("Form copy", fields.get("W2Copy"))
    print_field("Control number", fields.get("ControlNumber"))
    describe_party("Employee", fields.get("Employee"))
    describe_party("Employer", fields.get("Employer"))
    print("  Income and taxes")
    print_field("Wages, tips, other compensation", fields.get("WagesTipsAndOtherCompensation"))
    print_field("Federal income tax withheld", fields.get("FederalIncomeTaxWithheld"))
    print_field("Social Security wages", fields.get("SocialSecurityWages"))
    print_field("Social Security tax withheld", fields.get("SocialSecurityTaxWithheld"))
    print_field("Social Security tips", fields.get("SocialSecurityTips"))
    print_field("Medicare wages and tips", fields.get("MedicareWagesAndTips"))
    print_field("Medicare tax withheld", fields.get("MedicareTaxWithheld"))
    print_field("Allocated tips", fields.get("AllocatedTips"))
    print_field("Dependent care benefits", fields.get("DependentCareBenefits"))
    print_field("Non-qualified plans", fields.get("NonQualifiedPlans"))
    print_field("Verification code", fields.get("VerificationCode"))
    print_field("State wages, tips, etc.", fields.get("StateWagesTipsEtc"))
    print_field("State income tax", fields.get("StateIncomeTax"))
    print_field("Local wages, tips, etc.", fields.get("LocalWagesTipsEtc"))
    print_field("Local income tax", fields.get("LocalIncomeTax"))
    describe_additional_info(fields.get("AdditionalInfo"))
    print("  Flags")
    print_field("Statutory employee", fields.get("IsStatutoryEmployee"))
    print_field("Retirement plan", fields.get("IsRetirementPlan"))
    print_field("Third-party sick pay", fields.get("IsThirdPartySickPay"))
    print_field("Other notes", fields.get("Other"))


def main() -> None:
    parser = add_common_arguments(argparse.ArgumentParser(description="Analyze US W-2 tax forms."))
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
        print("No W-2 documents were returned.")
        return

    for index, document in enumerate(documents, start=1):
        describe_w2(document, index)


if __name__ == "__main__":
    main()
