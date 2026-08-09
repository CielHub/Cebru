import os
import shutil
import subprocess
import time
import json
import re
from pathlib import Path

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

LOGIN_URL = "https://tokoku.itemku.com/login"
DAGANGAN_URL = "https://tokoku.itemku.com/dagangan"
PROFILE_DIR = Path(__file__).parent / "browser" / "profile"
DATA_DIR = Path(__file__).parent / "data"
DEBUG_DIR = Path(__file__).parent / "debug"
PRODUCTS_FILE = DATA_DIR / "products.json"
DEBUG_TEXT = DEBUG_DIR / "dagangan_text.txt"
DEBUG_HTML = DEBUG_DIR / "dagangan.html"
DEBUG_SCREENSHOT = DEBUG_DIR / "dagangan.png"
DEBUG_PORT = 9222


def find_chrome():
    candidates = [
        os.environ.get("PROGRAMFILES", "") + r"\Google\Chrome\Application\chrome.exe",
        os.environ.get("PROGRAMFILES(X86)", "") + r"\Google\Chrome\Application\chrome.exe",
        os.environ.get("LOCALAPPDATA", "") + r"\Google\Chrome\Application\chrome.exe",
    ]
    for candidate in candidates:
        if candidate and Path(candidate).is_file():
            return Path(candidate)
    found = shutil.which("chrome.exe")
    if found:
        return Path(found)
    return None


def start_normal_chrome():
    chrome = find_chrome()
    if not chrome:
        raise RuntimeError(
            "Google Chrome tidak ditemukan. Install Google Chrome terlebih dahulu."
        )

    PROFILE_DIR.mkdir(parents=True, exist_ok=True)
    args = [
        str(chrome),
        f"--remote-debugging-port={DEBUG_PORT}",
        f"--user-data-dir={PROFILE_DIR}",
        "--start-maximized",
        LOGIN_URL,
    ]
    print(f"[→] Chrome: {chrome}")
    print("[→] Starting normal Google Chrome...")
    subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def wait_for_cdp(p, timeout_seconds=20):
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        try:
            return p.chromium.connect_over_cdp(f"http://127.0.0.1:{DEBUG_PORT}")
        except Exception:
            time.sleep(0.5)
    raise RuntimeError("Tidak bisa terhubung ke Chrome melalui CDP.")


def get_tokoku_page(context):
    for page in context.pages:
        if "tokoku.itemku.com" in page.url.lower():
            return page
    return context.pages[0] if context.pages else context.new_page()


def login_detected(page):
    if "tokoku.itemku.com/login" not in page.url.lower():
        return True
    try:
        return page.get_by_text("Daganganku", exact=True).count() > 0
    except Exception:
        return False


def wait_for_login(page, context):
    print("\n[Login]")
    print("  Jika belum login, klik 'Login dengan Google' dan selesaikan login manual.")
    print("  Bot tidak mengisi password/OTP/2FA.\n")

    deadline = time.time() + 180
    while time.time() < deadline:
        if login_detected(page):
            print("[✓] Tokoku login detected.")
            return True
        time.sleep(1)

    return False


def clean_text(value):
    return re.sub(r"\s+", " ", value or "").strip()


def parse_number(value):
    if value is None:
        return None
    digits = re.sub(r"[^\d]", "", value)
    return int(digits) if digits else None


def extract_candidates(page):
    """
    Phase 1 is deliberately read-only.

    We inspect visible product-like containers and use text heuristics for:
    - product name
    - price
    - stock
    - possible active/inactive labels

    The raw HTML/text is also saved so selectors can be hardened against the
    actual Tokoku UI before any future phase is allowed to change data.
    """
    body_text = clean_text(page.locator("body").inner_text(timeout=15000))
    DEBUG_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    DEBUG_TEXT.write_text(page.locator("body").inner_text(), encoding="utf-8")
    DEBUG_HTML.write_text(page.content(), encoding="utf-8")
    page.screenshot(path=str(DEBUG_SCREENSHOT), full_page=True)

    # Candidate containers. Prefer semantic rows/cards, then fall back to
    # elements containing both a currency amount and stock-related wording.
    locators = [
        page.locator("tr"),
        page.locator("[role='row']"),
        page.locator("article"),
        page.locator("[class*='product' i]"),
        page.locator("[class*='item' i]"),
    ]

    seen = set()
    candidates = []

    for locator in locators:
        try:
            count = min(locator.count(), 500)
        except Exception:
            continue

        for i in range(count):
            try:
                el = locator.nth(i)
                text = clean_text(el.inner_text(timeout=1000))
            except Exception:
                continue

            if len(text) < 8 or len(text) > 1200:
                continue

            # Require a price-like token and some product/listing context.
            has_price = bool(re.search(r"(?:Rp|IDR)\s*[\d.,]+", text, re.I))
            has_stock_word = bool(re.search(r"(stok|stock)", text, re.I))
            if not (has_price and has_stock_word):
                continue

            key = text[:700]
            if key in seen:
                continue
            seen.add(key)
            candidates.append(text)

    # Convert candidates to conservative records. If stock cannot be parsed,
    # keep the candidate for review rather than pretending it is eligible.
    products = []
    for idx, text in enumerate(candidates, start=1):
        prices = re.findall(r"(?:Rp|IDR)\s*[\d.,]+", text, re.I)
        stock_match = re.search(
            r"(?:stok|stock)\s*[:\-]?\s*(\d[\d.,]*)",
            text,
            re.I,
        )
        stock = parse_number(stock_match.group(1)) if stock_match else None
        price = parse_number(prices[0]) if prices else None

        products.append({
            "discovery_index": idx,
            "name": text,
            "price": price,
            "stock": stock,
            "eligible_stock": bool(stock is not None and stock > 0),
            "raw_text": text,
        })

    PRODUCTS_FILE.write_text(
        json.dumps(products, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return products


def show_summary(products):
    total = len(products)
    in_stock = sum(1 for p in products if p["eligible_stock"])
    unknown = sum(1 for p in products if p["stock"] is None)

    print("\n=== PHASE 1 · PRODUCT MANAGER ===")
    print(f"Candidates discovered : {total}")
    print(f"Stock > 0             : {in_stock}")
    print(f"Stock unknown         : {unknown}")
    print("\n[Read-only mode]")
    print("No stock, price, or product settings were changed.\n")

    if products:
        print("Discovered candidates:")
        for p in products[:100]:
            stock = "?" if p["stock"] is None else str(p["stock"])
            price = "?" if p["price"] is None else f"Rp{p['price']:,}".replace(",", ".")
            flag = "ELIGIBLE" if p["eligible_stock"] else "SKIP"
            print(f"  [{flag:8}] stock={stock:>4} price={price:>10} | {p['name'][:100]}")
    else:
        print("[!] No product candidates were confidently detected.")
        print("[!] Debug files were saved for selector refinement.")


def main():
    print("=== ITEMKU PRICE BOT · PHASE 1 ===")
    print("Baseline: Phase 0 Persistent Google Login")
    print("Mode: READ-ONLY Product Discovery")
    print(f"Login URL : {LOGIN_URL}")
    print(f"Product URL: {DAGANGAN_URL}\n")

    with sync_playwright() as p:
        start_normal_chrome()
        print("[→] Connecting to Chrome...")
        browser = wait_for_cdp(p)

        context = browser.contexts[0]
        page = get_tokoku_page(context)

        if not wait_for_login(page, context):
            print("[!] Login was not detected within 3 minutes.")
            input("Press ENTER to close...")
            browser.close()
            return

        print("[→] Opening Daganganku...")
        page.goto(DAGANGAN_URL, wait_until="domcontentloaded")
        page.wait_for_timeout(2000)

        print(f"[✓] Current page: {page.url}")
        print("[→] Reading product listings (read-only)...")

        products = extract_candidates(page)
        show_summary(products)

        print("\n[✓] Discovery complete.")
        print(f"[✓] Saved: {PRODUCTS_FILE}")
        print(f"[✓] Debug text: {DEBUG_TEXT}")
        print(f"[✓] Debug HTML: {DEBUG_HTML}")
        print(f"[✓] Debug screenshot: {DEBUG_SCREENSHOT}")

        input("\nPress ENTER to close the bot...")
        try:
            browser.close()
        except Exception:
            pass


if __name__ == "__main__":
    main()
