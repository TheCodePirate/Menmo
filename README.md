# Funding Assistant Experience

This repository hosts a static prototype of the Funding Assistant suite. The experience introduces a left-hand navigation shell
with a conversational Funding Assistant, portfolio home page, and supporting resources that cover grant programs, eligibility,
sustainability commitments, the application pipeline, and archived release notes. Every page is written with AI-guided funding
workflows in mind, including the requirement that assistant answers always cite the uploaded legal and policy documents.

## Running the site locally

Serve the contents of [`web/`](web/) using any static file server. With Python 3 installed you can run:

```bash
python3 -m http.server 8080 --directory web
```

Open <http://localhost:8080/> to launch the Funding Assistant. Navigate via the left menu to review grant resources or use the
Company Home link in the top-right corner to see portfolio status snapshots.
