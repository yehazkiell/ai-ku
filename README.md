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
