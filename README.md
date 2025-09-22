# Menmo

menmo.ai

## Samples

### Analyze document layout

This repository includes a sample script that demonstrates how to inspect layout data returned by the Azure AI Document Intelligence service.

1. Install the required dependency:

   ```bash
   pip install azure-ai-documentintelligence
   ```

2. Export your Document Intelligence resource credentials as environment variables:

   ```bash
   export AZURE_DOCUMENTINTELLIGENCE_ENDPOINT="<your-endpoint>"
   export AZURE_DOCUMENTINTELLIGENCE_KEY="<your-key>"
   ```

3. Run the sample against a local document:

   ```bash
   python samples/sample_analyze_layout.py path/to/document.pdf
   ```

Use `python samples/sample_analyze_layout.py --help` to see the available arguments. The script prints detected paragraphs, tables (including row/column spans), and the section hierarchy so you can explore the returned layout structure.
