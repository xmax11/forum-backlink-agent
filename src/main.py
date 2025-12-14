import os
import json
import time
from src.crawler.crawler import crawl_forum
from src.parser.thread_parser import extract_thread_data
from src.posting.poster import post_reply
from src.groq_client import generate_reply
import requests


# ✅ Google Sheet Logging
def log_to_sheet(forum, thread, status, message):
    url = os.getenv("SHEET_WEBHOOK_URL")
    if not url:
        print("No SHEET_WEBHOOK_URL configured, skipping log.")
        return

    payload = {
        "forum": forum,
        "thread": thread,
        "status": status,
        "message": message
    }

    try:
        requests.post(url, json=payload, timeout=10)
        print(f"Logged to sheet: {status} - {thread}")
    except Exception as e:
        print("Failed to send log:", e)


# ✅ Load forum config
def load_forum_config():
    with open("config/forums.yaml", "r") as f:
        import yaml
        return yaml.safe_load(f)


# ✅ Load processed threads
def load_processed_threads():
    try:
        with open("data/threads.json", "r") as f:
            return json.load(f).get("processed_threads", [])
    except:
        return []


# ✅ Save processed threads
def save_processed_thread(url):
    try:
        with open("data/threads.json", "r") as f:
            data = json.load(f)
    except:
        data = {"processed_threads": []}

    if url not in data["processed_threads"]:
        data["processed_threads"].append(url)

    with open("data/threads.json", "w") as f:
        json.dump(data, f, indent=2)


# ✅ Main Agent Logic
def run_agent():
    forums = load_forum_config()
    processed = load_processed_threads()

    for forum_name, forum_data in forums.items():
        print(f"\n--- Processing forum: {forum_name} ---")

        threads = crawl_forum(forum_data)

        for thread_url in threads:
            if thread_url in processed:
                print(f"Skipping already processed thread: {thread_url}")
                continue

            print(f"Parsing thread: {thread_url}")
            thread_text = extract_thread_data(thread_url)

            if not thread_text:
                print("Thread parsing failed.")
                log_to_sheet(forum_name, thread_url, "error", "Thread parsing failed")
                continue

            print("Generating reply...")
            reply = generate_reply(thread_text)

            if not reply:
                print("Reply generation failed.")
                log_to_sheet(forum_name, thread_url, "error", "Reply generation failed")
                continue

            print("Posting reply...")
            success = post_reply(forum_data, thread_url, reply)

            if success:
                print("✅ Reply posted successfully!")
                log_to_sheet(forum_name, thread_url, "success", "Reply posted successfully")
                save_processed_thread(thread_url)
            else:
                print("❌ Failed to post reply.")
                log_to_sheet(forum_name, thread_url, "error", "Failed to post reply")

            time.sleep(3)  # small delay between threads


if __name__ == "__main__":
    run_agent()
