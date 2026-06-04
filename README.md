# 🤖 AI-Ku Ultra IQ

AI-Ku adalah platform AI Suite profesional yang menyediakan layanan Chat LLM dan Image Generation secara **100% GRATIS** dan **TANPA API KEY**.

Platform ini dirancang untuk memberikan kecerdasan tingkat tinggi dengan antarmuka yang modern, responsif, dan kaya fitur.

## ✨ Fitur Utama

-   **🧠 Hazz Intelligence Series**:
    -   **Hazz-1 Thinking**: Model yang dirancang untuk berpikir mendalam (Chain-of-Thought) sebelum menjawab.
    -   **Hazz-1 Search**: Dilengkapi akses web real-time untuk jawaban paling update.
    -   **Hazz-1 Ultra**: Model IQ 300+ untuk penyelesaian masalah paling kompleks.
-   **📚 Learning Lab**: Kemampuan AI untuk mempelajari materi atau data yang Anda berikan sebelum mulai berdiskusi.
-   **🎨 Advanced Image Generation**: Membuat gambar berkualitas tinggi dengan model FLUX.1, Realism, dan lainnya. Dilengkapi dengan pengaturan rasio (1:1, 16:9, 9:16).
-   **🧪 Personality Lab**: Kustomisasi identitas AI Anda sendiri! Atur *System Prompt* untuk membuat AI yang tanpa batasan, edukatif, atau sesuai persona yang Anda inginkan.
-   **🔑 Developer API System**: Buat API Key Anda sendiri dan integrasikan kekuatan AI-Ku ke dalam aplikasi Anda melalui endpoint `/api/v1/`.
-   **💬 Multi-Chat Management**: Kelola banyak sesi chat secara bersamaan. Riwayat chat dan preferensi disimpan aman di browser Anda (*localStorage*).
-   **🎙 Voice Interaction**: Mendukung *Speech-to-Text* (Input Suara) dan *Text-to-Speech* (AI Berbicara).
-   **💻 Pro Coding Experience**: Rendering Markdown yang cantik dengan syntax highlighting (highlight.js) dan tombol "Copy" sekali klik.
-   **🌙 Dark & Light Mode**: Pilih tema yang nyaman untuk mata Anda.

## 🛠 Instalasi Lokal

Pastikan Anda memiliki Python 3.10+ terinstal.

1.  **Clone Repositori**:
    ```bash
    git clone https://github.com/yehazkiell/ai-ku.git
    cd ai-ku
    ```

2.  **Instal Dependensi**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Jalankan Aplikasi**:
    ```bash
    python app.py
    ```

4.  **Akses UI**: Buka browser Anda dan kunjungi `http://localhost:5000`.

## 🚀 Penggunaan API untuk Developer

Dapatkan API Key di tab **Developer** pada aplikasi, lalu gunakan seperti ini:

```bash
curl -X POST http://localhost:5000/api/v1/chat \
-H "Authorization: Bearer YOUR_API_KEY" \
-H "Content-Type: application/json" \
-d '{"message": "Halo AI, apa kabar?", "engine": "ultra"}'
```

## 📜 Lisensi
Proyek ini dilisensikan di bawah lisensi MIT.

---
*Dibuat dengan ❤️ oleh yehazkiell & Jules AI.*
