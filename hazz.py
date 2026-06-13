#!/usr/bin/env python3
import sys
import os
import time
from core import get_ai_response, run_team_task, generate_image, save_data, NEURAL_MATRIX
from registry import AGENT_REGISTRY

def clear(): os.system('cls' if os.name == 'nt' else 'clear')

def logo():
    print("""\033[96m
    █████╗ ██╗      ██╗  ██╗██╗   ██╗
    ██╔══██╗██║      ██║ ██╔╝██║   ██║
    ███████║██║█████╗█████╔╝ ██║   ██║
    ██╔══██╗██║╚════╝██╔═██╗ ██║   ██║
    ██║  ██║██║      ██║  ██╗╚██████╔╝
    ╚═╝  ╚═╝╚═╝      ╚═╝  ╚═╝ ╚═════╝
    \033[91m[ AI-KU: ULTRA-HEAVY EDITION (100GB+ RAM READY) ]\033[0m
    """)

def main():
    clear()
    logo()
    current_role = 'coder'

    while True:
        try:
            prompt = input(f"\033[94mULTRA({current_role}) » \033[0m").strip()
            if not prompt: continue
            if prompt.lower() in ['/exit', 'exit']: break

            if prompt.startswith('/learn '):
                save_data(prompt[7:])
                print("\033[92mInjected into Neural Matrix.\033[0m")
                continue

            # Standard Intelligence Loop (Team Based)
            print(f"\033[90m[Matrix] Parallel reasoning in progress...\033[0m", end="\r")
            response = run_team_task(prompt)
            print("\033[K", end="")
            print(f"\n\033[91mAI-KU-ULTRA »\033[0m\n{response}\n")

        except KeyboardInterrupt: break
        except Exception as e: print(f"Error: {e}")

if __name__ == "__main__":
    main()
