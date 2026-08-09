# Itemku Price Bot - Phase 0

Phase 0 khusus untuk **persistent browser session** Tokoku menggunakan Python + Playwright.

## Tujuan

- Membuka `tokoku.itemku.com` dengan Chromium.
- Login Google dilakukan **manual** oleh seller.
- Tidak ada password Google yang disimpan oleh script.
- Session/cookies/storage disimpan di profile Chromium lokal.
- Run berikutnya menggunakan profile yang sama sehingga tidak perlu login ulang selama session masih valid.

## Instalasi Windows

Dari folder project:

```powershell
python -m pip install -r requirements.txt
python -m playwright install chromium
```

## Jalankan

```powershell
python main.py
```

## Login pertama kali

1. Chromium akan terbuka.
2. Login ke Tokoku menggunakan Google secara manual.
3. Selesaikan OTP/2FA/CAPTCHA jika Google memintanya.
4. Pastikan sudah masuk sebagai seller.
5. Kembali ke terminal.
6. Tekan **ENTER**.
7. Browser ditutup dan profile session tetap disimpan.

## Run berikutnya

Jalankan lagi:

```powershell
python main.py
```

Playwright akan membuka Chromium dengan profile yang sama.

## Struktur

```text
itemku_price_bot_phase0/
├── main.py
├── config.json
├── requirements.txt
├── README.md
├── .gitignore
└── browser/
    └── profile/       # dibuat otomatis, JANGAN dibagikan
```

## Keamanan

- Jangan memasukkan password Google ke `config.json` atau source code.
- Jangan membagikan folder `browser/profile`.
- Jangan upload `browser/profile` ke GitHub/cloud.
- Folder profile sudah dimasukkan ke `.gitignore`.
- Jika session kedaluwarsa, login ulang secara manual.

## Batas Phase 0

Belum ada:

- membaca daftar produk,
- filter stok/produk aktif,
- scan kompetitor,
- update harga,
- auto-reprice,
- auto-chat.

Fitur tersebut masuk phase berikutnya setelah persistent login terbukti stabil.
