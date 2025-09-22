# Menmo

menmo.ai

## Samples

### Analyze text with Document Intelligence

The sample script in `samples/sample_analyze_read.py` demonstrates how to use the Azure
Document Intelligence prebuilt Read model to extract printed and handwritten text lines.

```bash
export AZURE_DOCUMENTINTELLIGENCE_ENDPOINT="https://<your-resource-name>.cognitiveservices.azure.com/"
export AZURE_DOCUMENTINTELLIGENCE_KEY="<your-key>"
python samples/sample_analyze_read.py <path-or-url-to-document>
```

Replace the environment variable values and the argument with your resource details and
the document you want to analyze.
