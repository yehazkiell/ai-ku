import sys
import os
import time
from core import get_ai_response, run_team_task, start_scout_mode, get_clarifying_questions

def clear(): os.system('cls' if os.name == 'nt' else 'clear')

def logo():
    print("""\033[96m
    █████╗ ██╗      ██╗  ██╗██╗   ██╗
    ██╔══██╗██║      ██║ ██╔╝██║   ██║
    ███████║██║█████╗█████╔╝ ██║   ██║
    ██╔══██╗██║╚════╝██╔═██╗ ██║   ██║
    ██║  ██║██║      ██║  ██╗╚██████╔╝
    ╚═╝  ╚═╝╚═╝      ╚═╝  ╚═╝ ╚═════╝
    \033[93m[ AI-KU: Team & Scout Edition ]\033[0m
    """)

def main():
    clear()
    logo()
    start_scout_mode()

    print("Selamat datang! Masukkan namamu untuk memulai.")
    name = input("User >> ").strip() or "User"
    print(f"\nHalo {name}! AI-KU siap bekerja.\n")

    while True:
        try:
            prompt = input(f"\033[94m{name} >> \033[0m").strip()
            if not prompt: continue
            if prompt.lower() in ['/exit', 'exit', 'quit']: break

            # Interactive Questions
            print(f"\033[90m[Oracle] Sedang menganalisis tugas...\033[0m")
            qs = get_clarifying_questions(prompt)
            print("\n\033[93mMohon jawab pertanyaan ini dulu agar saya lebih pintar (Minimal 5):")
            answers = []
            for i, q in enumerate(qs[:5]):
                ans = input(f" {q} >> ")
                answers.append(ans)

            # Multi-Agent Execution
            full_task = f"{prompt}. Detail tambahan: {' '.join(answers)}"
            response = run_team_task(full_task)

            print(f"\n\033[92m[AI-KU Result] >>\033[0m\n{response}\n")

        except KeyboardInterrupt: break
        except Exception as e: print(f"Error: {e}")

if __name__ == "__main__":
    main()
