from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

LOGIN_URL = "https://tokoku.itemku.com/login"
PROFILE_DIR = Path(__file__).parent / "browser" / "profile"

def is_logged_in(page):
    if "tokoku.itemku.com/login" not in page.url.lower():
        return True
    try:
        return page.get_by_text("Daganganku", exact=True).count() > 0
    except Exception:
        return False

def main():
    print("=== ITEMKU PRICE BOT - PHASE 0 ===")
    print("Browser: Google Chrome (installed on this PC)")
    print(f"Login URL: {LOGIN_URL}\n")

    PROFILE_DIR.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        print("[→] Opening Google Chrome...")
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE_DIR),
            channel="chrome",
            headless=False,
            viewport=None,
            args=["--start-maximized"],
        )

        page = context.pages[0] if context.pages else context.new_page()

        print("[→] Opening Tokoku login...")
        page.goto(LOGIN_URL, wait_until="domcontentloaded")

        print("\nIf you are not logged in:")
        print("  1. Login to Tokoku using Google manually.")
        print("  2. Complete OTP / 2FA / CAPTCHA if Google asks.")
        print("  3. Make sure you are back inside your Tokoku seller account.\n")

        input("Press ENTER after login is complete...")

        try:
            page.wait_for_load_state("domcontentloaded", timeout=10000)
        except PlaywrightTimeoutError:
            pass
        page.wait_for_timeout(1500)

        if is_logged_in(page):
            print("[✓] Login/session detected.")
            print("[✓] Persistent browser profile is saved.")
            print(f"[✓] Profile: {PROFILE_DIR}")
        else:
            print("[!] The browser still appears to be on the login page.")
            print("[!] Session was kept, but Phase 0 cannot confirm login yet.")

        input("\nPress ENTER to close the browser...")
        context.close()

if __name__ == "__main__":
    main()
