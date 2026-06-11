# AI-KU (PRO EDITION) 🚀

Platform AI serbaguna yang dioptimalkan untuk performa, keamanan, dan efisiensi RAM (~200MB).

## ✨ Keunggulan
- **Multi-Provider Fallback**: Otomatis berpindah provider jika salah satu gagal (G4F, Pollinations).
- **Security First**: API terproteksi API Key, Rate Limiting, dan Sandbox Execution.
- **Observability**: Logging terpusat dan health checks.
- **Production Ready**: Docker support dan CI/CD pipeline terintegrasi.
- **Project Forge**: Kemampuan mengelola file proyek via CLI.

## 🚀 Instalasi Cepat

### Menggunakan Python Lokal
```bash
./install.sh
python3 app.py # Untuk API
python3 hazz.py # Untuk CLI
```

### Menggunakan Docker
```bash
docker-compose up -d
```

## 🔌 API Integration (REST)

Akses API di `http://localhost:5000/api/v1/chat`.

**Header Wajib**:
- `X-API-KEY`: Master key kamu (setel di `.env`).
- `Content-Type`: `application/json`.

**Contoh Payload**:
```json
{
  "message": "Analisis file ini",
  "role": "coder"
}
```

## 🛠️ CLI Commands
- `/role [type]` : Ganti role AI.
- `/learn [fact]` : Simpan memori permanen.
- `/ls`           : List file proyek.
- `/exit`         : Keluar.

## 📦 Lisensi
MIT - 2024 AI-Ku Team
