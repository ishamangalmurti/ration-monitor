import requests
from bs4 import BeautifulSoup
import hashlib
import os
import sys
import time

URL = "https://ahara.karnataka.gov.in/NRC/app_offline_current.aspx"

HASH_FILE = "last_hash.txt"

MAX_RETRIES = 3


def clean_page_content(html):
    soup = BeautifulSoup(html, "html.parser")

    for tag in soup(["script", "style"]):
        tag.decompose()

    text = soup.get_text(separator=" ", strip=True)

    return " ".join(text.split())


def get_hash(content):
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def load_previous_hash():
    if not os.path.exists(HASH_FILE):
        return None

    with open(HASH_FILE, "r") as f:
        return f.read().strip()


def save_hash(hash_value):
    with open(HASH_FILE, "w") as f:
        f.write(hash_value)


def fetch_page():

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/122.0 Safari/537.36"
        )
    }

    for attempt in range(MAX_RETRIES):

        try:
            response = requests.get(
                URL,
                headers=headers,
                timeout=60
            )

            response.raise_for_status()

            return response.text

        except requests.exceptions.RequestException as e:

            print(f"Attempt {attempt + 1} failed: {e}")

            if attempt < MAX_RETRIES - 1:
                time.sleep(15)

    return None


html = fetch_page()

if html is None:
    print("Could not reach website.")
    sys.exit(0)


content = clean_page_content(html)

current_hash = get_hash(content)

previous_hash = load_previous_hash()

if previous_hash is None:

    save_hash(current_hash)

    print("Initial hash saved.")

    sys.exit(0)


if current_hash != previous_hash:

    print("CHANGE_DETECTED")

    save_hash(current_hash)

    sys.exit(1)

print("No change.")