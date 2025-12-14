import requests
from bs4 import BeautifulSoup


def fetch_thread(url):
    """
    Fetches a forum thread URL and returns its HTML content.
    """
    try:
        response = requests.get(url, timeout=15, headers={
            "User-Agent": "Mozilla/5.0 (Backlink-Agent)"
        })
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"[ThreadParser] Error fetching thread {url}: {e}")
        return ""


def extract_thread_title(soup):
    """
    Attempts to extract the thread title from common forum platforms.
    """
    # XenForo
    title = soup.find("h1", class_="p-title-value")
    if title:
        return title.get_text(strip=True)

    # phpBB / vBulletin / MyBB / SMF / IPS / Vanilla
    generic = soup.find("title")
    if generic:
        return generic.get_text(strip=True)

    return "Untitled Thread"


def extract_thread_text(soup):
    """
    Extracts visible text from the first post of a thread.
    Works across multiple forum platforms.
    """
    # XenForo
    xf_post = soup.find("article", class_="message-body")
    if xf_post:
        return xf_post.get_text(" ", strip=True)

    # phpBB
    phpbb_post = soup.find("div", class_="content")
    if phpbb_post:
        return phpbb_post.get_text(" ", strip=True)

    # Discourse
    discourse_post = soup.find("div", class_="post")
    if discourse_post:
        return discourse_post.get_text(" ", strip=True)

    # Fallback: extract all text
    return soup.get_text(" ", strip=True)


def parse_thread(url):
    """
    Fetches and parses a forum thread.
    Returns:
        (title, text)
    """
    html = fetch_thread(url)
    if not html:
        return ("Untitled Thread", "")

    soup = BeautifulSoup(html, "html.parser")

    title = extract_thread_title(soup)
    text = extract_thread_text(soup)

    return (title, text)
