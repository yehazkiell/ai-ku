#!/usr/bin/env python3
import os

from core import (
    get_ai_response,
    run_team_task,
    generate_image,
    save_data,
    recall_data,
)
from aiku.agents.registry import MODEL_MATRIX
from aiku.config import settings


def clear():
    os.system('cls' if os.name == 'nt' else 'clear')


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


HELP_TEXT = """\033[95mCommands:\033[0m
  /help              Show this help
  /models            List the AI-KU model matrix
  /config            Show current configuration (secrets masked)
  /chat <message>    Single-turn RAG-augmented chat (no autonomous tools)
  /plan <task>       Run the autonomous Plan->Act->Observe->Reflect agent
  /image <prompt>    Generate an image URL
  /remember <text>   Save a fact to long-term memory
  /recall <query>    Search long-term memory
  /search <query>    Web search via the agent
  /exit              Quit
Anything else is treated as an autonomous agent task."""


def main():
    clear()
    logo()
    print("\n\033[95mAI-KU:\033[0m Professional Software Engineer, Researcher & Automation Agent.")
    print("\033[90mFollowing Priority: Search -> Browser -> Terminal -> File Ops\033[0m")
    print("\033[90mType /help for commands.\033[0m\n")

    while True:
        try:
            prompt = input("\033[94mAI-KU » \033[0m").strip()
            if not prompt:
                continue

            lower = prompt.lower()
            if lower in ('/exit', 'exit', '/quit'):
                break

            if lower == '/help':
                print(HELP_TEXT)
                continue

            if lower == '/models':
                for cat, models in MODEL_MATRIX.items():
                    print(f"\n\033[95m{cat}:\033[0m")
                    for m, d in models.items():
                        print(f"  - {m}: {d.get('tokens', d.get('res', d.get('desc', 'Active')))}")
                continue

            if lower == '/config':
                print(f"\n\033[95mConfiguration:\033[0m\n{settings.summary()}")
                continue

            if lower.startswith('/chat '):
                msg = prompt[len('/chat '):].strip()
                print(f"\n\033[92m[AI-KU] »\033[0m\n{get_ai_response(msg)}\n")
                continue

            if lower.startswith('/image '):
                p = prompt[len('/image '):].strip()
                print(f"\n\033[92m[IMAGE] »\033[0m {generate_image(p)}\n")
                continue

            if lower.startswith('/remember '):
                text = prompt[len('/remember '):].strip()
                print(f"\033[92m[MEMORY] »\033[0m {save_data(text)}")
                continue

            if lower.startswith('/recall '):
                q = prompt[len('/recall '):].strip()
                results = recall_data(q)
                if results:
                    for r in results:
                        print(f"  - {r}")
                else:
                    print("  (no memories found)")
                continue

            if lower.startswith('/search '):
                q = prompt[len('/search '):].strip()
                print(run_team_task(f"Search the web and summarize: {q}", role="researcher"))
                continue

            task = prompt[len('/plan '):].strip() if lower.startswith('/plan ') else prompt
            response = run_team_task(task)
            print(f"\n\033[92m[FINAL REPORT] »\033[0m\n{response}\n")

        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    main()
