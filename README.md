# AI-KU (INTELLIGENT EDITION v4.0) 🚀

Platform AI serbaguna yang ditenagai oleh **Real RAG (Retrieval-Augmented Generation)** dan **Multi-Agent Orchestration**. Dioptimalkan untuk performa tinggi, keamanan, dan persistensi data.

## ✨ Fitur Utama
- **Real Vector Memory**: Menggunakan ChromaDB dan Sentence-Transformers untuk ingatan jangka panjang yang akurat dan persisten.
- **Autonomous Multi-Agent Loop**: Kolaborasi antara Researcher, Analyst, dan Lead Lead untuk menyelesaikan tugas kompleks.
- **True RAG Integration**: Setiap respon diperkaya dengan data lokal (Memori) dan data global (Web Search).
- **Professional API**: Validasi skema (Pydantic), Rate Limiting, dan Error Handling terstruktur.
- **Hazz Sandbox**: Eksekusi logika Python aman dalam lingkungan terisolasi.

## 🚀 Instalasi

### Prasyarat
- Python 3.12+
- RAM 8GB+ (Disarankan 16GB+ untuk performa maksimal RAG lokal)

### Setup Cepat
```bash
./install.sh
python3 app.py # Jalankan API Professional
python3 hazz.py # Jalankan CLI Advanced
```

## 🔌 Dokumentasi API (REST)

**Endpoint**: `POST /api/v1/chat`
**Header**: `X-API-KEY: your_key`

**Body**:
```json
{
  "message": "Apa itu RAG?",
  "role": "researcher"
}
```

## 🛠️ CLI Power Commands
- `/ls`      : Lihat struktur proyek.
- `/learn`   : Ajarkan AI fakta baru (disimpan ke Vector DB).
- `/models`  : Daftar model Godmode tersedia.

## 📦 Lisensi
MIT - 2024 AI-Ku Professional Team
