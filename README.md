# Itemku Price Bot - Phase 1 · Product Manager

Phase 1 is **READ-ONLY**.

It preserves the locked Phase 0 login architecture:
- normal installed Google Chrome
- direct `https://tokoku.itemku.com/login`
- manual Google OAuth
- persistent profile in `browser/profile`
- Playwright connects to Chrome via CDP

After login, Phase 1 opens:

```text
https://tokoku.itemku.com/dagangan
```

It attempts to discover product/listing candidates and filter products with
`stock > 0`.

## Important

This phase does **not**:
- change prices
- change stock
- click save/update
- scan itemku.com competitors

Raw page data is saved under `debug/` to let us harden selectors against the
actual Tokoku page before moving to the next phase.

## Setup

```cmd
python -m pip install -r requirements.txt
python main.py
```

No `playwright install chromium` is required.

## Output

- `data/products.json`
- `debug/dagangan_text.txt`
- `debug/dagangan.html`
- `debug/dagangan.png`

`browser/profile/` must never be committed to GitHub.
