# Itemku Price Bot - Phase 0

Phase 0 handles persistent Google/Tokoku login only.

This version launches the **Google Chrome installed on the PC** using Playwright's `channel="chrome"`, not Playwright's bundled Chromium/Chrome for Testing.

## Setup

```cmd
python -m pip install -r requirements.txt
```

You do **not** need `playwright install chromium` for this version.

Run:

```cmd
python main.py
```

First run:
1. Chrome opens.
2. Bot opens `https://tokoku.itemku.com/login`.
3. Login with Google manually.
4. Complete OTP/2FA/CAPTCHA yourself if requested.
5. Return to CMD and press ENTER.
6. The persistent browser profile is saved under `browser\profile`.

Later runs reuse that profile.

## Security

Never upload or share `browser\profile\`. It contains the browser session.
Do not store Google passwords, OTP codes, or 2FA secrets in the project.
