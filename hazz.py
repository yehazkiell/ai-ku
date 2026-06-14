#!/usr/bin/env python3
import sys
import os
import time
from core import get_ai_response, run_team_task, generate_image, save_data
from aiku.agents.registry import MODEL_MATRIX

def clear(): os.system('cls' if os.name == 'nt' else 'clear')

def logo():
    print("""\033[96m
    █████╗ ██╗      ██╗  ██╗██╗   ██╗
    ██╔══██╗██║      ██║ ██╔╝██║   ██║
    ███████║██║█████╗█████╔╝ ██║   ██║
    ██╔══██╗██║╚════╝██╔═██╗ ██║   ██║
    ██║  ██║██║      ██║  ██╗╚██████╔╝
    ╚═╝  ╚═╝╚═╝      ╚═╝  ╚═╝ ╚═════╝
    \033[93m[ AI-KU: AUTONOMOUS AGENT EDITION v4.5 ]\033[0m
    """)

def main():
    clear()
    logo()
    print("\n\033[95mAI-KU:\033[0m Professional Software Engineer, Researcher & Automation Agent.")
    print("\033[90mFollowing Priority: Search -> Browser -> Terminal -> File Ops\033[0m\n")

    while True:
        try:
            prompt = input(f"\033[94mAI-KU » \033[0m").strip()
            if not prompt: continue
            if prompt.lower() in ['/exit', 'exit']: break

            if prompt == '/models':
                for cat, models in MODEL_MATRIX.items():
                    print(f"\n\033[95m{cat}:\033[0m")
                    for m, d in models.items():
                        print(f"  - {m}: {d.get('tokens', d.get('res', 'Active'))}")
                continue

            # Autonomous Multi-Agent Loop
            response = run_team_task(prompt)
            print(f"\n\033[92m[FINAL REPORT] »\033[0m\n{response}\n")

        except KeyboardInterrupt: break
        except Exception as e: print(f"Error: {e}")

if __name__ == "__main__":
    main()
