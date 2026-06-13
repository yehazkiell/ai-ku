#!/usr/bin/env python3
import sys
import os
import time
from core import get_ai_response, run_team_task, generate_image
from registry import MODEL_MATRIX

def clear(): os.system('cls' if os.name == 'nt' else 'clear')

def logo():
    print("""\033[91m
    █████╗ ██╗      ██╗  ██╗██╗   ██╗
    ██╔══██╗██║      ██║ ██╔╝██║   ██║
    ███████║██║█████╗█████╔╝ ██║   ██║
    ██╔══██╗██║╚════╝██╔═██╗ ██║   ██║
    ██║  ██║██║      ██║  ██╗╚██████╔╝
    ╚═╝  ╚═╝╚═╝      ╚═╝  ╚═╝ ╚═════╝
    [ AI-KU: GODMODE EDITION (100GB+ RAM) ]
    \033[0m""")

def main():
    clear()
    logo()
    print("\n\033[93mModel Matrix Aktif. Pilih kategori model atau ketik langsung pesanmu.\033[0m")

    while True:
        try:
            prompt = input(f"\033[94mAI-KU-GOD » \033[0m").strip()
            if not prompt: continue
            if prompt.lower() in ['/exit', 'exit']: break

            if prompt == '/models':
                for cat, models in MODEL_MATRIX.items():
                    print(f"\n\033[95m{cat}:\033[0m")
                    for m, d in models.items():
                        print(f"  - {m}: {d.get('tokens', d.get('res', 'Active'))}")
                continue

            print(f"\033[90m[Oracle] Processing in Godmode...\033[0m", end="\r")
            response = run_team_task(prompt)
            print("\033[K", end="")
            print(f"\n\033[91mAI-KU-OMNI »\033[0m\n{response}\n")

        except KeyboardInterrupt: break
        except Exception as e: print(f"Error: {e}")

if __name__ == "__main__":
    main()
