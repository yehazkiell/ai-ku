import sys
import os
import time
from core import get_ai_response, run_team_task, forge_edit_file, generate_image
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
    \033[93m[ AI-KU: Forge & Terminal Edition ]\033[0m
    """)

def list_files(path='.'):
    print("\n\033[95m📁 PROJECT STRUCTURE:\033[0m")
    for root, dirs, files in os.walk(path):
        if '.git' in dirs: dirs.remove('.git')
        if '__pycache__' in dirs: dirs.remove('__pycache__')
        level = root.replace(path, '').count(os.sep)
        indent = ' ' * 4 * (level)
        print(f"{indent}{os.path.basename(root)}/")
        subindent = ' ' * 4 * (level + 1)
        for f in files:
            print(f"{subindent}{f}")

def main():
    clear()
    logo()

    current_role = 'coder'

    while True:
        try:
            prompt = input(f"\033[94mAI-KU ({current_role}) >> \033[0m").strip()
            if not prompt: continue
            if prompt.lower() in ['/exit', 'exit']: break

            if prompt.lower() == '/ls':
                list_files()
                continue

            if prompt.startswith('/role '):
                role = prompt.split(' ')[1].lower()
                if role in AGENT_REGISTRY:
                    current_role = role
                    print(f"\033[92m[Sistem] Role beralih ke {role.upper()}\033[0m")
                else:
                    print(f"\033[91mRole tidak ditemukan. Pilihan: {', '.join(AGENT_REGISTRY.keys())}\033[0m")
                continue

            if prompt.startswith('/write '):
                parts = prompt.split(' ', 2)
                if len(parts) < 3:
                    print("\033[91mGunakan: /write [file] [konten]\033[0m")
                else:
                    res = forge_edit_file(parts[1], parts[2])
                    print(f"\033[92m{res}\033[0m")
                continue

            if prompt.startswith('/image '):
                print("\033[93m🎨 Menggenerasi visual...\033[0m")
                url = generate_image(prompt[7:])
                print(f"\033[92mLink: {url}\033[0m")
                continue

            # Standard Intelligence Loop (Team Based)
            print(f"\033[90m[Forge] Menjalankan tim AI-KU...\033[0m")
            response = run_team_task(prompt)
            print(f"\n\033[92m[Result] >>\033[0m\n{response}\n")

        except KeyboardInterrupt: break
        except Exception as e: print(f"Error: {e}")

if __name__ == "__main__":
    main()
