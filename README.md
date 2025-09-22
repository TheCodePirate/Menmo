# Menmo

menmo.ai

## Document Intelligence samples

The `samples/` folder contains command line utilities that demonstrate how to call
Azure Document Intelligence prebuilt models for invoices, identity documents,
receipts, and US W-2 tax forms. Each script accepts either a local file path or an
HTTPS/SAS URL via the `--document` argument and prints the most important fields in a
readable format.

### Prerequisites

* Python 3.8 or later.
* Install the SDK dependency:

  ```bash
  pip install azure-ai-documentintelligence
  ```

* An Azure Document Intelligence resource endpoint and API key.

Each command accepts optional `--locale` and `--pages` parameters so you can control
language hints and the page range submitted to the service.

### Invoice analysis

Analyze a local invoice:

```bash
python samples/sample_analyze_invoices.py \
  --endpoint https://<resource>.cognitiveservices.azure.com \
  --key <api-key> \
  --document ./invoices/contoso-invoice.pdf \
  --locale en-US
```

Analyze an invoice stored behind a SAS URL:

```bash
python samples/sample_analyze_invoices.py \
  --endpoint https://<resource>.cognitiveservices.azure.com \
  --key <api-key> \
  --document "https://storageaccount.blob.core.windows.net/documents/invoice.pdf?<sas-token>"
```

### Identity document analysis

```bash
python samples/sample_analyze_identity_documents.py \
  --endpoint https://<resource>.cognitiveservices.azure.com \
  --key <api-key> \
  --document ./ids/license.jpg
```

```bash
python samples/sample_analyze_identity_documents.py \
  --endpoint https://<resource>.cognitiveservices.azure.com \
  --key <api-key> \
  --document "https://storageaccount.blob.core.windows.net/ids/passport.png?<sas-token>"
```

### Receipt analysis

```bash
python samples/sample_analyze_receipts.py \
  --endpoint https://<resource>.cognitiveservices.azure.com \
  --key <api-key> \
  --document ./receipts/contoso-allinone.jpg
```

```bash
python samples/sample_analyze_receipts.py \
  --endpoint https://<resource>.cognitiveservices.azure.com \
  --key <api-key> \
  --document "https://storageaccount.blob.core.windows.net/receipts/store-receipt.jpg?<sas-token>"
```

### US W-2 tax form analysis

```bash
python samples/sample_analyze_tax_us_w2.py \
  --endpoint https://<resource>.cognitiveservices.azure.com \
  --key <api-key> \
  --document ./taxforms/sample_w2.png \
  --locale en-US
```

```bash
python samples/sample_analyze_tax_us_w2.py \
  --endpoint https://<resource>.cognitiveservices.azure.com \
  --key <api-key> \
  --document "https://storageaccount.blob.core.windows.net/tax/w2.png?<sas-token>" \
  --locale en-US
```
