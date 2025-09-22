# Menmo
menmo.ai

## Azure Document Intelligence add-on samples

The `samples/` folder contains standalone Python scripts that demonstrate how to enable each Azure Document Intelligence add-on. Every script configures a `DocumentIntelligenceClient`, submits an analysis request with the desired feature, and prints the add-on specific section of the response.

### Prerequisites

1. Use Python 3.11 or later.
2. Install the SDK dependency:

   ```bash
   python -m pip install azure-ai-documentintelligence
   ```

3. Export your Document Intelligence resource credentials before running any sample:

   ```bash
   export DOCUMENTINTELLIGENCE_ENDPOINT="https://<your-resource>.cognitiveservices.azure.com/"
   export DOCUMENTINTELLIGENCE_KEY="<your-key>"
   ```

4. Provide either a local file path or a publicly accessible URL for the document you want to analyze.

### Running the samples

Run the commands from the repository root. Each script accepts a document source and an optional `--model-id` argument (defaulting to `prebuilt-layout` unless otherwise noted).

- **Barcodes (`samples/sample_analyze_addon_barcodes.py`)**

  ```bash
  python samples/sample_analyze_addon_barcodes.py path/to/barcode.pdf
  ```

  Prints every detected barcode value together with its type, confidence score, and polygon coordinates.

- **Font metadata (`samples/sample_analyze_addon_fonts.py`)**

  ```bash
  python samples/sample_analyze_addon_fonts.py path/to/document.pdf
  ```

  Lists the detected font family hints, style/weight details, handwriting detection, and color information for each styled span.

- **Formulas (`samples/sample_analyze_addon_formulas.py`)**

  ```bash
  python samples/sample_analyze_addon_formulas.py https://contoso.com/math-notes.png
  ```

  Reports the formulas found on each page, including whether they are inline or block formulas, their confidence, and their bounding polygons.

- **High-resolution bounding boxes (`samples/sample_analyze_addon_highres.py`)**

  ```bash
  python samples/sample_analyze_addon_highres.py path/to/scan.pdf --max-words 10
  ```

  Displays the high-resolution polygon for each word (up to the specified limit) so you can visualize the precise OCR coordinates returned by the add-on.

- **Language detection (`samples/sample_analyze_addon_languages.py`)**

  ```bash
  python samples/sample_analyze_addon_languages.py path/to/multilingual.pdf
  ```

  Shows the detected language locale, its confidence score, and a sample of the text span associated with each detection.

- **Query fields (`samples/sample_analyze_addon_query_fields.py`)**

  ```bash
  python samples/sample_analyze_addon_query_fields.py path/to/invoice.pdf --model-id prebuilt-invoice --query "What is the invoice total?" --query "Who is the vendor?"
  ```

  Executes the supplied natural-language queries and prints the extracted answers, including confidence values and bounding regions. The script provides invoice-related default queries when `--query` arguments are omitted.

Each script raises a clear error if the required environment variables are missing or if the document cannot be loaded. Review the console output to understand how each add-on enriches the base analysis payload.
