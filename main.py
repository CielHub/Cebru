from pathlib import Path
from playwright.sync_api import sync_playwright

BASE_DIR = Path(__file__).resolve().parent
PROFILE_DIR = BASE_DIR / "browser" / "profile"
TOKOKU_URL = "https://tokoku.itemku.com/"
PROFILE_DIR.mkdir(parents=True, exist_ok=True)


def main():
    print("=" * 58)
    print("           ITEMKU PRICE BOT - PHASE 0")
    print("        Persistent Google Login / Browser Session")
    print("=" * 58)
    print(f"[i] Profile : {PROFILE_DIR}")
    print("[i] Browser : Chromium / Playwright")
    print()
    print("Phase 0 TIDAK menyimpan password Google.")
    print("Login, OTP/2FA, atau CAPTCHA tetap dilakukan manual.")
    print()

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE_DIR),
            headless=False,
            viewport={"width": 1365, "height": 900},
            args=["--start-maximized"],
        )

        page = context.pages[0] if context.pages else context.new_page()
        print("[→] Membuka Tokoku...")
        page.goto(TOKOKU_URL, wait_until="domcontentloaded", timeout=60000)

        try:
            page.wait_for_load_state("networkidle", timeout=15000)
        except Exception:
            pass

        print("[✓] Browser terbuka.")
        print()
        print("Jika belum login:")
        print("  1. Login Tokoku menggunakan Google secara manual.")
        print("  2. Selesaikan OTP/2FA/CAPTCHA jika diminta Google.")
        print("  3. Pastikan kamu sudah masuk ke akun seller Tokoku.")
        print()
        print("Jika sudah login dari run sebelumnya, cukup pastikan halaman sudah terbuka.")
        input("Tekan ENTER untuk menyimpan session dan menutup browser... ")

        # Menunggu sebentar agar perubahan cookie/storage selesai ditulis.
        page.wait_for_timeout(1000)

        print()
        print("[✓] Session/profile tersimpan.")
        print(f"[✓] Lokasi profile: {PROFILE_DIR}")
        print("[i] Run berikutnya akan memakai profile yang sama.")
        print("[i] Jangan bagikan folder browser/profile karena berisi session browser.")

        context.close()


if __name__ == "__main__":
    main()
