# mediumscraper

This repository contains a small example script for scraping Medium.

The script `image_size_scraper.py` searches <https://doejistar.medium.com/> for
posts that include the word *week* in the title. For each matched article it
collects all images and computes the total size of those images. Results are
printed in a human-readable format (bytes, KB, MB, etc.).

Usage:

```bash
pip install -r requirements.txt  # install dependencies
python image_size_scraper.py
```

The scraper sends requests with a browser-like User-Agent header and uses a
timeout of 10 seconds for each HTTP request.

> **Note:** Access to the target Medium domain may be blocked in some
environments (including Codex). If the script fails with a connection error,
you may need to allow outbound traffic to `doejistar.medium.com` or run the
script from a network that can reach the site.
