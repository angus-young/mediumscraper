"""Scraper for calculating total size of images in each weekly Medium post.

This script searches https://doejistar.medium.com/ for posts whose title
contains the word "week". For each such post it downloads the page,
collects all image URLs and sums the size of the images. The size is
retrieved using HTTP HEAD (falling back to GET if Content-Length is
missing).

The script prints the total size in bytes for each matched post.

Network access to doejistar.medium.com may be restricted in the Codex
execution environment so running this script may fail unless that domain
is allowed. The logic is kept to illustrate how it would normally work.
"""

import re
import sys
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

# Reuse a single session to enable connection pooling and provide a user-agent
_SESSION = requests.Session()
_SESSION.headers.update(
    {
        "User-Agent": (
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/123.0 Safari/537.36"
        )
    }
)

DEFAULT_TIMEOUT = 10

BASE_URL = "https://doejistar.medium.com"


def get_weekly_posts():
    """Return a list of (title, url) for posts containing 'week' in the title."""
    resp = _SESSION.get(BASE_URL, timeout=DEFAULT_TIMEOUT)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    posts = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        title = a.get_text(strip=True)
        if "/p/" in href and re.search(r"week", title, re.I):
            posts.append((title, urljoin(BASE_URL, href)))
    return posts


def get_image_size(url):
    """Return the size in bytes for the image at ``url``."""
    head = _SESSION.head(url, allow_redirects=True, timeout=DEFAULT_TIMEOUT)
    if head.status_code == 200 and head.headers.get("Content-Length"):
        return int(head.headers["Content-Length"])
    get = _SESSION.get(url, timeout=DEFAULT_TIMEOUT)
    get.raise_for_status()
    return len(get.content)


def total_images_size(article_url):
    """Sum the size of all images in a Medium article."""
    resp = _SESSION.get(article_url, timeout=DEFAULT_TIMEOUT)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    total = 0
    for img in soup.find_all("img", src=True):
        src = img["src"]
        if src.startswith("data:"):
            continue
        total += get_image_size(urljoin(article_url, src))
    return total


def format_bytes(num):
    """Return a human-readable size string for ``num`` bytes."""
    for unit in ("bytes", "KB", "MB", "GB"):
        if num < 1024:
            return f"{num:.0f} {unit}" if unit == "bytes" else f"{num:.2f} {unit}"
        num /= 1024
    return f"{num:.2f} TB"


def main():
    try:
        posts = get_weekly_posts()
    except Exception as exc:
        print(f"Failed to fetch posts: {exc}", file=sys.stderr)
        return 1
    for title, url in posts:
        try:
            size = total_images_size(url)
            print(f"{title} -> {format_bytes(size)}")
        except Exception as exc:
            print(f"Failed to fetch images for {url}: {exc}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
