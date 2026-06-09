# AI-Ku Hazz Series (CLI & API Edition) 🚀

AI Chatbot cerdas yang dioptimalkan untuk **RAM Rendah (~200MB)**. 100% gratis, tanpa API Key, dan memiliki fitur search gratis.

## ✨ Fitur Utama
- **Dual Mode**: Gunakan via Terminal (`hazz.py`) atau sebagai API untuk Bot (`app.py`).
- **Low RAM Footprint**: Dirancang khusus agar ringan (~200MB RAM) untuk server kecil.
- **Hazz-1 Intelligence**: Model Ultra, Thinking, Search (Web), dan Vision (PDF/TXT).
- **Free Search & Images**: Akses informasi real-time dan generate gambar (Flux) tanpa biaya.

## 🚀 Instalasi

```bash
git clone https://github/yehazkiell/ai-ku
cd ai-ku
./install.sh
```

## 🤖 Penggunaan via API (Untuk Bot)

Jalankan server:
```bash
python3 app.py
```

Contoh Request:
```python
import requests

payload = {
    "message": "Siapa juara F1 2023?",
    "model": "hazz-1-search"
}
response = requests.post("http://localhost:5000/api/v1/chat", json=payload)
print(response.json()['response'])
```

## 💻 Penggunaan via CLI

Jalankan terminal AI:
```bash
python3 hazz.py
```

Gunakan perintah `/help` untuk navigasi.

## 📦 Lisensi
MIT - 2024 AI-Ku Team

## 🧠 Hazz Intelligence Extensions (New!)
Fitur spesial yang saya tambahkan untuk meningkatkan kemampuan analisis:
1. **Hazz Brain**: Memori jangka panjang yang tersimpan di `memory.json`. Gunakan `/learn` untuk mengajari AI.
2. **Hazz Sandbox**: Eksekusi logika Python via `/run`. Berguna untuk perhitungan presisi.
3. **Hazz Monitor**: Pantau penggunaan resource server via `/sys`.
4. **Enhanced Search**: Algoritma pencarian yang lebih dalam dan terstruktur.

## 🤖 Hazz Mini-Agent (New!)
Fitur ini memungkinkan AI bekerja secara otonom untuk menyelesaikan tugas kompleks.
- **CLI**: `/agent [tugas kamu]`
- **API**: `/api/v1/agent`
- **Cara Kerja**: Agent akan melakukan riset (Search), menjalankan logika (Sandbox), dan merangkum hasilnya secara mandiri.

## 🏟️ Hazz Arena (Inspirasi Arena AI)
Kamu bisa memanggil agen spesialis untuk tugas yang sangat spesifik.
- **CLI**: `/arena [role] [tugas]`
- **Role Tersedia**: `researcher`, `coder`, `architect`, `writer`, `general`.
- **API**: Tambahkan field `"role": "coder"` pada payload `/api/v1/agent`.
- **Artifacts**: Agen akan mencatat progress di `agent_workspace.txt`.

---

## 🔌 Panduan Integrasi (Bot / System)

Kamu bisa menghubungkan AI-Ku ke bot Discord, Telegram, atau sistem kustom milikmu dengan sangat mudah.

### 1. Menjalankan Server API
Gunakan perintah berikut di server/VPS kamu:
```bash
python3 app.py
```
Server akan berjalan di `http://0.0.0.0:5000` dengan konsumsi RAM yang sangat rendah (~200MB).

### 2. Endpoint Chat Biasa
**POST** `/api/v1/chat`
```json
{
  "message": "Halo, siapa kamu?",
  "model": "hazz-1-ultra"
}
```

### 3. Endpoint Agent Otonom (Arena AI Style)
**POST** `/api/v1/agent`
```json
{
  "task": "Buatkan rencana belajar Python dalam 7 hari",
  "role": "coder"
}
```
*Role tersedia: `coder`, `researcher`, `architect`, `writer`, `general`.*

### 4. Endpoint Generate Gambar
**POST** `/api/v1/generate-image`
```json
{
  "prompt": "Cyberpunk city in 4k"
}
```

---

## 🚀 Cara Menghubungkan Bot Kamu (Integration Guide)

Jika kamu pemilik bot (Discord, Telegram, WhatsApp) dan ingin menggunakan kecerdasan AI-Ku, ikuti langkah berikut:

### 1. Persiapan Server
AI-Ku sangat ringan, bisa jalan di VPS spesifikasi paling rendah sekalipun (hanya butuh **~200MB RAM**).
1. Pastikan server kamu sudah menginstall Python.
2. Jalankan API: `python3 app.py` (Default port: 5000).

### 2. Contoh Kodingan untuk Bot (Python / discord.py)
```python
import discord
import requests
from discord.ext import commands

bot = commands.Bot(command_prefix="!")

@bot.command()
async def tanya(ctx, *, pesan):
    # Kirim request ke AI-Ku API
    payload = {"message": pesan, "model": "hazz-1-ultra"}
    response = requests.post("http://IP_SERVER_KAMU:5000/api/v1/chat", json=payload)

    data = response.json()
    await ctx.send(data['response'])

bot.run("TOKEN_DISCORD_KAMU")
```

### 3. Contoh Kodingan untuk Bot (Node.js / discord.js)
```javascript
const { Client, GatewayIntentBits } = require('discord.js');
const axios = require('axios');

const client = new Client({ intents: [GatewayIntentBits.GuildMessages, GatewayIntentBits.MessageContent, GatewayIntentBits.Guilds] });

client.on('messageCreate', async (message) => {
    if (message.content.startsWith('!tanya')) {
        const prompt = message.content.replace('!tanya ', '');

        const response = await axios.post('http://IP_SERVER_KAMU:5000/api/v1/chat', {
            message: prompt,
            model: 'hazz-1-search' // Bisa pakai mode search gratis!
        });

        message.reply(response.data.response);
    }
});

client.login('TOKEN_DISCORD_KAMU');
```

### 💡 Tips Bot Owner
- **Tanpa API Key**: Kamu tidak butuh key apapun, cukup arahkan ke IP server tempat kamu menjalankan `app.py`.
- **Hemat Biaya**: AI ini 100% gratis selamanya.
- **Mode Agent**: Gunakan endpoint `/api/v1/agent` jika ingin bot kamu bisa melakukan riset otonom sebelum menjawab.

---
