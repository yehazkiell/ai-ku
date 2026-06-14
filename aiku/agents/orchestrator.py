import g4f
import json
import re
from loguru import logger
from aiku.tools.search import search_web
from aiku.tools.terminal import run_command
from aiku.tools.files import read_file, write_file, list_project_files
from aiku.memory.rag import memory_instance

class ExecutionEngine:
    """Parses and executes multi-tool actions from agent responses."""

    @staticmethod
    def execute_action(action_str):
        # Expected format: ACTION: [TYPE] ARGS: [DATA]
        try:
            match = re.search(r'ACTION:\s*(\w+)\s*ARGS:\s*(.*)', action_str, re.DOTALL)
            if not match: return None

            action_type = match.group(1).upper()
            args = match.group(2).strip()

            if action_type == "TERMINAL":
                return f"[TERMINAL OUTPUT]\n{run_command(args)}"
            elif action_type == "READ":
                return f"[FILE CONTENT]\n{read_file(args)}"
            elif action_type == "WRITE":
                # Splitting file and content: format: [path] | [content]
                path, content = args.split('|', 1)
                return write_file(path.strip(), content.strip())
            elif action_type == "SEARCH":
                return search_web(args)
            return f"Unknown action: {action_type}"
        except Exception as e:
            return f"Execution Error: {str(e)}"

class AutonomousOrchestrator:
    def __init__(self):
        self.history = []

    def call_llm(self, prompt, system_msg="You are AI-KU."):
        messages = [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": prompt}
        ]
        # Attempt multiple providers for stability
        providers = [(g4f.Provider.OperaAria, g4f.models.gpt_4), (g4f.Provider.Blackbox, g4f.models.gpt_4)]
        for provider, model in providers:
            try:
                return g4f.ChatCompletion.create(model=model, provider=provider, messages=messages)
            except Exception as e:
                logger.error(f"Inference error with {provider.__name__}: {e}")
                continue
        return "Critical Error: All providers failed."

    def run_task(self, task):
        print(f"\n\033[96m[AI-KU] Target: {task}\033[0m")
        context = ""

        # Max 5 loops for autonomous execution
        for i in range(5):
            print(f"\033[90m[Iteration {i+1}/5] Thinking...\033[0m", end="\r")

            prompt = f"TASK: {task}\nCONTEXT: {context}\n\nWhat is your next action? Choose one:\n1. ACTION: TERMINAL ARGS: [command]\n2. ACTION: READ ARGS: [filepath]\n3. ACTION: WRITE ARGS: [filepath] | [content]\n4. ACTION: SEARCH ARGS: [query]\n5. ACTION: FINISH ARGS: [final report]\n\nReply ONLY with the action format."

            response = self.call_llm(prompt)
            print("\033[K", end="")

            if "FINISH" in response:
                report = response.split("ARGS:")[1].strip()
                memory_instance.add_memory(f"Task: {task} | Result: {report}")
                return report

            print(f"\033[93m[Action] {response.split('ARGS:')[0]}\033[0m")
            result = ExecutionEngine.execute_action(response)
            context += f"\n--- Action Result ---\n{result}\n"

        return "Task stopped: Max iterations reached."

orchestrator = AutonomousOrchestrator()
