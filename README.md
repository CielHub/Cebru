# Itemku Price Bot - Phase 0 Revision 2

## Goal

Phase 0 only handles persistent Tokoku/Google login.

This revision does **not** let Playwright launch Chromium/Chrome for Testing.
Instead:

1. The installed Google Chrome (`chrome.exe`) is launched directly.
2. Chrome uses a dedicated local profile under `browser\profile`.
3. Playwright connects to that already-running Chrome through CDP.
4. You manually perform the Google OAuth login.
5. The profile is reused on future runs.

This avoids using Playwright's bundled Chromium/Chrome for Testing.

## Setup

```cmd
python -m pip install -r requirements.txt
```

No `playwright install chromium` is required.

Run:

```cmd
python main.py
```

The browser opens directly at:

```text
https://tokoku.itemku.com/login
```

Then manually click **Login dengan Google** and complete the login.

## Important

Use the dedicated Chrome window opened by the script. Do not use your normal everyday Chrome profile for this bot.

The session is stored locally in:

```text
browser\profile\
```

Do NOT upload or share that directory.

Do not put Google passwords, OTP codes, or 2FA secrets into the project.

## Git

Recommended `.gitignore` entries:

```gitignore
browser/profile/
__pycache__/
*.pyc
.env
logs/
data/local/
```
