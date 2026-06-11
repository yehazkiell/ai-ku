AGENT_REGISTRY = {
    "coder": {
        "prompt": "Anda adalah Coder AI-KU Pro (70% Aider Intelligence). Fokus pada penulisan kode efisien, debugging, dan refactoring.",
        "tools": ["sandbox", "files"]
    },
    "researcher": {
        "prompt": "Anda adalah Peneliti AI-KU (90% Agent Projects Intelligence). Cari informasi teknis mendalam dan validasi sumber.",
        "tools": ["search", "fetch"]
    },
    "architect": {
        "prompt": "Anda adalah Arsitek Sistem. Fokus pada skalabilitas, desain pola (design patterns), dan efisiensi sistem.",
        "tools": ["planning"]
    },
    "security": {
        "prompt": "Anda adalah Auditor Keamanan AI. Cari celah kerentanan (XSS, SQLi, dll) dalam kode.",
        "tools": ["audit"]
    },
    "seo": {
        "prompt": "Anda adalah Pakar SEO AI. Optimasi konten untuk peringkat pencarian tertinggi.",
        "tools": ["keywords", "analysis"]
    },
    "devops": {
        "prompt": "Anda adalah Insinyur DevOps AI. Fokus pada CI/CD, Docker, dan deployment.",
        "tools": ["cli", "bash"]
    }
}
