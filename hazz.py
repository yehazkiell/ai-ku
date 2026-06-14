#!/usr/bin/env python3
import sys
import os
import time
from core import get_ai_response, run_team_task, generate_image
from aiku.agents.registry import MODEL_MATRIX

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


            if user_input.startswith('/manus '):
                task = user_input[7:].strip()
                from manus.engine import manus_instance
                print(f"\033[95m[Manus] Mengaktifkan General Purpose Agent...\033[0m")
                response = manus_instance.execute_general_task(task)
                print(f"\n\033[96m[Manus Result] »\033[0m")
                from core import get_ai_response # for print_slow type effect if I had one globally, else just print
                print(response)
                print()
                continue

            if user_input.startswith('/manus-upgrade '):
                parts = user_input.split(' ')
                if len(parts) < 3:
                    print("\033[91mGunakan: /manus-upgrade [skill] [level]\033[0m")
                    continue
                skill = parts[1]
                level = parts[2]
                from manus.engine import manus_instance
                msg = manus_instance.upgrade_skill(skill, level)
                print(f"\033[92m[Manus] {msg}\033[0m\n")
                continue

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
