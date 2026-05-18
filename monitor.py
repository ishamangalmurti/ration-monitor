import requests
from bs4 import BeautifulSoup
import hashlib
import os
import sys

URL = "https://ahara.karnataka.gov.in/NRC/app_offline_current.aspx"

HASH_FILE = "last_hash.txt"


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


response = requests.get(
    URL,
    headers={"User-Agent": "Mozilla/5.0"},
    timeout=30
)

content = clean_page_content(response.text)

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