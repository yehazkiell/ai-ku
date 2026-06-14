# AI-KU (AUTONOMOUS AGENT EDITION) 🤖

AI-KU adalah agen AI otonom bergaya **Manus AI, Devin AI, dan Jules AI** dengan
akses ke Terminal, Sistem File, Sandbox Python, Pencarian Web, Memori vektor
(RAG), dan generasi gambar. Dirancang untuk bekerja layaknya Software Engineer &
Peneliti tingkat lanjut: **Plan → Act → Observe → Reflect → Report**.

Tersedia dalam dua antarmuka:
- **CLI** — `python3 hazz.py`
- **REST API** — `python3 app.py` (Flask)

---

## ✨ Fitur Utama

- **Agen Otonom (Plan→Act→Observe→Reflect)** — membuat rencana eksplisit,
  mengeksekusi tool satu per satu, mengamati hasil, lalu mengkritik diri
  (reflection) sebelum melanjutkan.
- **RAG-Augmented Intelligence** — menarik memori relevan dari vektor store
  (ChromaDB) dan riwayat percakapan untuk jawaban yang sadar konteks.
- **Router LLM Multi-Provider** — OpenRouter → Groq → OpenAI → g4f (gratis),
  dengan fallback otomatis bila satu provider gagal.
- **Toolbelt** — Terminal, File (baca/tulis/list), Sandbox Python, Web Search,
  Image Generation.
- **REST API profesional** — validasi Pydantic, rate limiting, API key.
- **Konfigurasi terpusat** — semua diatur lewat variabel lingkungan.

---

## 📜 10 Aturan Emas AI-KU
1. Selalu berpikir langkah-demi-langkah.
2. Gunakan pencarian web sebelum membuat asumsi.
3. Gunakan Browser/tool jika hasil pencarian kurang memadai.
4. Inspeksi codebase sebelum melakukan perubahan kode.
5. Gunakan perintah terminal yang aman.
6. Alur kerja: Search → Analyze → Plan → Execute → Verify → Report.
7. Pilih solusi paling handal jika ada banyak opsi.
8. Berikan update progres secara berkala.
9. Nyatakan ketidakpastian secara jelas jika data tidak terverifikasi.
10. Bertindak profesional, akurat, efisien, dan aman.

---

## 🚀 Instalasi

### Prasyarat
- Python **3.12+**
- `pip` dan (disarankan) `venv`
- Opsional: Docker & Docker Compose

### Opsi A — Instalasi lokal (venv, disarankan)
```bash
git clone https://github.com/yehazkiell/ai-ku.git
cd ai-ku

python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

pip install -r requirements.txt
```

### Opsi B — Skrip cepat
```bash
./install.sh
```

### Opsi C — Docker
```bash
cp .env.example .env             # lalu sunting .env (lihat di bawah)
docker compose up --build
# API tersedia di http://localhost:5000
```

> Catatan: dependensi RAG (`chromadb`, `sentence-transformers`) cukup besar dan
> akan mengunduh model embedding `all-MiniLM-L6-v2` saat **pertama kali** memori
> digunakan. CLI/API tetap bisa jalan tanpa langkah ini berkat *lazy loading*.

---

## ⚙️ Konfigurasi Variabel Lingkungan

Salin templat lalu sunting:
```bash
cp .env.example .env
```

| Variabel | Default | Wajib? | Keterangan |
|---|---|---|---|
| `AIKU_API_KEY` | `aiku_master_key_123` | **Ya (produksi)** | Kunci untuk header `X-API-KEY` di setiap request API. Ganti di produksi. |
| `AIKU_ENV` | `development` | Tidak | `development` / `production`. Mode produksi memunculkan peringatan ketat. |
| `OPENROUTER_API_KEY` | _(kosong)_ | Tidak | Kunci OpenRouter. Jika diisi, dipakai lebih dulu. |
| `GROQ_API_KEY` | _(kosong)_ | Tidak | Kunci Groq. |
| `OPENAI_API_KEY` | _(kosong)_ | Tidak | Kunci OpenAI. |
| `AIKU_LLM_PROVIDER` | `auto` | Tidak | `auto` / `openrouter` / `groq` / `openai` / `g4f`. |
| `AIKU_LLM_MODEL` | `gpt-4o-mini` | Tidak | Nama model yang dikirim ke provider. |
| `AIKU_REQUEST_TIMEOUT` | `60` | Tidak | Timeout (detik) panggilan LLM. |
| `AIKU_MAX_ITERATIONS` | `6` | Tidak | Maksimum iterasi loop agen otonom. |
| `AIKU_ENABLE_REFLECTION` | `true` | Tidak | Aktifkan langkah self-critique. |
| `AIKU_MEMORY_PATH` | `./chroma_db` | Tidak | Lokasi penyimpanan memori vektor. |
| `AIKU_MEMORY_TOP_K` | `4` | Tidak | Jumlah memori relevan yang ditarik. |
| `AIKU_HOST` | `0.0.0.0` | Tidak | Host server API. |
| `AIKU_PORT` | `5000` | Tidak | Port server API. |

> **Tanpa kunci provider apa pun**, AI-KU otomatis memakai provider gratis (g4f).
> Untuk stabilitas terbaik, isi minimal salah satu dari `OPENROUTER`/`GROQ`/`OPENAI`.

Cek konfigurasi aktif (nilai rahasia otomatis disamarkan):
```bash
python3 -c "from aiku.config import settings; print(settings.summary())"
# atau dari dalam CLI: ketik /config
```

---

## 🖥️ Penggunaan CLI

```bash
python3 hazz.py
```

Perintah yang tersedia:

| Perintah | Fungsi |
|---|---|
| `/help` | Tampilkan bantuan |
| `/models` | Daftar matriks model AI-KU |
| `/config` | Tampilkan konfigurasi (rahasia disamarkan) |
| `/chat <pesan>` | Chat sekali jalan dengan konteks RAG |
| `/plan <tugas>` | Jalankan agen otonom Plan→Act→Observe→Reflect |
| `/image <prompt>` | Hasilkan URL gambar |
| `/remember <teks>` | Simpan fakta ke memori jangka panjang |
| `/recall <query>` | Cari di memori jangka panjang |
| `/search <query>` | Pencarian web lewat agen |
| `/exit` | Keluar |

Teks lain dianggap sebagai tugas otonom.

---

## 🌐 Penggunaan REST API

Jalankan server:
```bash
python3 app.py
```

Semua endpoint (kecuali `/health` dan `/metrics`) memerlukan header
`X-API-KEY: <AIKU_API_KEY>`.

| Method | Endpoint | Deskripsi |
|---|---|---|
| `GET` | `/health` | Status & kapabilitas |
| `GET` | `/metrics` | Info konfigurasi runtime |
| `POST` | `/api/v1/chat` | Chat RAG-augmented |
| `POST` | `/api/v1/agent` | Tugas agen otonom |
| `POST` | `/api/v1/image` | Generasi gambar |
| `POST` | `/api/v1/memory` | Simpan memori |
| `GET` | `/api/v1/memory?q=...` | Cari memori |

Contoh:
```bash
# Health
curl http://localhost:5000/health

# Chat
curl -X POST http://localhost:5000/api/v1/chat \
  -H "X-API-KEY: aiku_master_key_123" \
  -H "Content-Type: application/json" \
  -d '{"message": "Jelaskan apa itu RAG", "role": "researcher"}'

# Agen otonom
curl -X POST http://localhost:5000/api/v1/agent \
  -H "X-API-KEY: aiku_master_key_123" \
  -H "Content-Type: application/json" \
  -d '{"task": "Buat skrip python penghitung bilangan prima", "role": "coder"}'

# Gambar
curl -X POST http://localhost:5000/api/v1/image \
  -H "X-API-KEY: aiku_master_key_123" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "kucing astronot, gaya digital art", "width": 1024, "height": 1024}'

# Memori
curl -X POST http://localhost:5000/api/v1/memory \
  -H "X-API-KEY: aiku_master_key_123" \
  -H "Content-Type: application/json" \
  -d '{"text": "Proyek ini memakai Flask dan ChromaDB."}'

curl "http://localhost:5000/api/v1/memory?q=Flask" -H "X-API-KEY: aiku_master_key_123"
```

---

## 🧪 Pengembangan & Pengujian

```bash
python3 -m unittest discover tests -v   # jalankan semua tes
python3 -c "import core; print('OK')"   # verifikasi inti
```

CI (GitHub Actions) menjalankan suite tes pada setiap push & pull request.

---

## 🏗️ Arsitektur

```
hazz.py            CLI / entry point
app.py             REST API (Flask)
core.py            API tingkat tinggi (chat, agent, memory, image)
aiku/
  config.py        Konfigurasi terpusat (env vars + validasi)
  llm.py           Router LLM multi-provider
  agents/
    orchestrator.py  Loop Plan→Act→Observe→Reflect
    registry.py      Matriks model & registry agen
  memory/rag.py    Memori vektor (ChromaDB, lazy-load)
  tools/           terminal, files, sandbox, search, image, browser, git
```

---

## 📦 Lisensi
MIT — lihat [LICENSE](LICENSE).
