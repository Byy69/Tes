# Panduan Setup Bot Discord Welcome

## Langkah 1: Buat Aplikasi Discord Bot

1. Buka https://discord.com/developers/applications
2. Klik "New Application" dan beri nama bot Anda (misalnya "Welcome Bot")
3. Klik "Create"

## Langkah 2: Setup Bot

1. Di sidebar kiri, klik "Bot"
2. Klik "Reset Token" untuk membuat token baru
3. **SALIN TOKEN INI** - Anda sudah memasukkannya ke Replit Secrets

## Langkah 3: Aktifkan Privileged Intents (PENTING!)

Di halaman Bot, scroll ke bawah ke bagian "Privileged Gateway Intents":

✅ **AKTIFKAN** opsi berikut:
- **MESSAGE CONTENT INTENT** - agar bot bisa membaca pesan command
- **SERVER MEMBERS INTENT** - agar bot bisa tahu ada member baru bergabung

Tanpa ini, bot tidak akan bekerja!

## Langkah 4: Set Permissions Bot

1. Di sidebar kiri, klik "OAuth2" → "URL Generator"
2. Centang "bot" di bagian Scopes
3. Di bagian Bot Permissions, centang:
   - Send Messages
   - Attach Files
   - Embed Links
   - Manage Guild (untuk setup command)

## Langkah 5: Undang Bot ke Server

1. Salin URL yang muncul di bagian bawah
2. Buka URL tersebut di browser
3. Pilih server Discord Anda dan klik "Authorize"

## Langkah 6: Setup Channel Welcome

Setelah bot masuk ke server:

1. Ketik `!setwelcome #nama-channel` untuk mengatur channel welcome
2. Ketik `!testwelcome` untuk test gambar welcome
3. Ketik `!welcomehelp` untuk melihat semua command

## Troubleshooting

Jika bot tidak merespon:
1. Pastikan Privileged Intents sudah diaktifkan
2. Pastikan bot punya permission Send Messages
3. Restart bot Discord di Replit (klik tombol restart)