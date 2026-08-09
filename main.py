import os
import shutil
import subprocess
import time
from pathlib import Path

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

LOGIN_URL = "https://tokoku.itemku.com/login"
PROFILE_DIR = Path(__file__).parent / "browser" / "profile"
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

    # Chrome is launched directly as the normal installed browser.
    # Playwright only connects to it afterward through CDP.
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

    return chrome


def wait_for_cdp(p, timeout_seconds=20):
    deadline = time.time() + timeout_seconds

    while time.time() < deadline:
        try:
            browser = p.chromium.connect_over_cdp(
                f"http://127.0.0.1:{DEBUG_PORT}"
            )
            return browser
        except Exception:
            time.sleep(0.5)

    raise RuntimeError(
        "Tidak bisa terhubung ke Chrome melalui CDP. "
        "Pastikan Chrome berhasil dibuka."
    )


def get_tokoku_page(context):
    pages = context.pages

    for page in pages:
        if "tokoku.itemku.com" in page.url.lower():
            return page

    return pages[0] if pages else context.new_page()


def login_detected(page):
    url = page.url.lower()

    if "tokoku.itemku.com/login" not in url:
        return True

    # A seller page element is a stronger signal than URL alone.
    try:
        if page.get_by_text("Daganganku", exact=True).count() > 0:
            return True
    except Exception:
        pass

    return False


def print_open_pages(context):
    print("\n[Pages]")
    for i, page in enumerate(context.pages, start=1):
        try:
            print(f"  {i}. {page.url}")
        except Exception:
            print(f"  {i}. <unavailable>")
    print()


def main():
    print("=== ITEMKU PRICE BOT - PHASE 0 REVISION 2 ===")
    print("Mode: Normal Google Chrome + CDP")
    print(f"Login URL: {LOGIN_URL}")
    print(f"Persistent profile: {PROFILE_DIR}")
    print()

    with sync_playwright() as p:
        start_normal_chrome()

        print("[→] Connecting to Chrome...")
        browser = wait_for_cdp(p)

        context = browser.contexts[0]
        page = get_tokoku_page(context)

        print("[✓] Connected to normal Chrome.")
        print(f"[✓] Current page: {page.url}")
        print()
        print("Login instructions:")
        print("  1. Di halaman Tokoku, klik 'Login dengan Google' sendiri.")
        print("  2. Jika popup Google muncul, selesaikan login di popup tersebut.")
        print("  3. Selesaikan OTP/2FA/CAPTCHA sendiri jika diminta.")
        print("  4. Jangan tutup Chrome selama proses login.")
        print()

        # We do not click the Google login button automatically.
        # The user performs the OAuth interaction in the normal browser.
        deadline = time.time() + 180

        last_page_count = len(context.pages)

        while time.time() < deadline:
            if login_detected(page):
                print("[✓] Tokoku login detected.")
                print("[✓] Persistent profile is stored.")
                print(f"[✓] Profile: {PROFILE_DIR}")
                break

            if len(context.pages) != last_page_count:
                print("[→] Browser page/popup changed.")
                print_open_pages(context)
                last_page_count = len(context.pages)

            # If OAuth opened a new page, inspect it without taking control
            # away from the user.
            for candidate in context.pages:
                try:
                    if "accounts.google.com" in candidate.url.lower():
                        print(f"[→] Google page detected: {candidate.url}")
                except Exception:
                    pass

            time.sleep(1)
        else:
            print("[!] Login was not detected within 3 minutes.")
            print_open_pages(context)

        print()
        input("Press ENTER to finish Phase 0 and close the bot...")

        try:
            browser.close()
        except Exception:
            pass


if __name__ == "__main__":
    main()
