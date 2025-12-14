import requests
from bs4 import BeautifulSoup


def fetch_url(url):
    """
    Fetches a URL and returns its HTML content.
    """
    try:
        response = requests.get(url, timeout=15, headers={
            "User-Agent": "Mozilla/5.0 (Backlink-Agent)"
        })
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"[Crawler] Error fetching {url}: {e}")
        return ""


def extract_visible_text(html):
    """
    Extracts visible text from HTML content.
    Removes scripts, styles, and hidden elements.
    """
    soup = BeautifulSoup(html, "html.parser")

    # Remove non-content tags
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    # Extract text
    text = soup.get_text(separator=" ")

    # Clean whitespace
    text = " ".join(text.split())
    return text


def crawl_domain(domain_url):
    """
    Crawls the main domain page and extracts clean text.
    This is used for anchor generation.
    """
    html = fetch_url(domain_url)
    if not html:
        return ""

    return extract_visible_text(html)
