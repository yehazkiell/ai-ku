import sys
import os
import time
import logging
from core import get_ai_response, run_team_task, generate_image, save_data
from registry import AGENT_REGISTRY
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.ERROR)

def clear(): os.system('cls' if os.name == 'nt' else 'clear')

def logo():
    print("""\033[96m
    █████╗ ██╗      ██╗  ██╗██╗   ██╗
    ██╔══██╗██║      ██║ ██╔╝██║   ██║
    ███████║██║█████╗█████╔╝ ██║   ██║
    ██╔══██╗██║╚════╝██╔═██╗ ██║   ██║
    ██║  ██║██║      ██║  ██╗╚██████╔╝
    ╚═╝  ╚═╝╚═╝      ╚═╝  ╚═╝ ╚═════╝
    \033[93m[ AI-KU: PRO EDITION ]\033[0m
    """)

def main():
    clear()
    logo()
    current_role = 'coder'

    while True:
        try:
            prompt = input(f"\033[94m{current_role} » \033[0m").strip()
            if not prompt: continue
            if prompt.lower() in ['/exit', 'exit']: break

            if prompt.startswith('/role '):
                role = prompt.split(' ')[1].lower()
                if role in AGENT_REGISTRY:
                    current_role = role
                    print(f"\033[92mRole changed to {role.upper()}\033[0m")
                continue

            if prompt.startswith('/learn '):
                fact = prompt[7:].strip()
                save_data(fact)
                print("\033[92mKnowledge stored.\033[0m")
                continue

            # API Call
            print("\033[90mProcessing...\033[0m", end="\r")
            response = get_ai_response(prompt, role=current_role)
            print("\033[K", end="")
            print(f"\n\033[92mAI »\033[0m\n{response}\n")

        except KeyboardInterrupt: break
        except Exception as e: print(f"\033[91mError: {e}\033[0m")

if __name__ == "__main__":
    main()
