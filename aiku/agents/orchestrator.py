"""Autonomous orchestrator for AI-KU.

Implements a Manus / Devin / Jules-style agent loop:

    PLAN  ->  ACT  ->  OBSERVE  ->  REFLECT  ->  (repeat)  ->  FINISH

The agent first drafts an explicit plan, then iterates: it picks one tool
action, runs it, observes the result, and (optionally) reflects/self-critiques
before continuing. Relevant long-term memories are retrieved (RAG) and injected
into the prompt for context-aware reasoning.
"""
import re

from loguru import logger

from aiku.config import settings
from aiku.llm import chat
from aiku.memory.rag import memory_instance
from aiku.tools.files import list_project_files, read_file, write_file
from aiku.tools.image import generate_image
from aiku.tools.sandbox import execute_python
from aiku.tools.search import search_web
from aiku.tools.terminal import run_command

PERSONA = (
    "You are AI-KU, an elite autonomous software engineer and researcher in the "
    "spirit of Devin, Manus, and Jules. You think step by step, verify facts with "
    "tools before asserting them, write reliable code, and clearly state any "
    "uncertainty. You follow the workflow: Search -> Analyze -> Plan -> Execute -> "
    "Verify -> Report, and you always prefer the most robust solution."
)

ROLE_PROMPTS = {
    "general": PERSONA,
    "coder": PERSONA + " Focus on architecture, clean code, and correctness.",
    "researcher": PERSONA + " Focus on thorough, well-cited research.",
    "guardian": PERSONA + " Focus on defensive security and secure coding.",
    "analyst": PERSONA + " Focus on rigorous verification and reflection.",
}

ACTION_MENU = (
    "Choose exactly ONE next action and reply ONLY in this format:\n"
    "  ACTION: TERMINAL ARGS: <shell command>\n"
    "  ACTION: READ ARGS: <filepath>\n"
    "  ACTION: WRITE ARGS: <filepath> | <content>\n"
    "  ACTION: SEARCH ARGS: <query>\n"
    "  ACTION: PYTHON ARGS: <python code, set `result`>\n"
    "  ACTION: IMAGE ARGS: <image prompt>\n"
    "  ACTION: LIST ARGS: <directory>\n"
    "  ACTION: FINISH ARGS: <final report>"
)


class ExecutionEngine:
    """Parses and executes a single tool action from an agent response."""

    @staticmethod
    def execute_action(action_str):
        try:
            match = re.search(r"ACTION:\s*(\w+)\s*ARGS:\s*(.*)", action_str, re.DOTALL)
            if not match:
                return None

            action_type = match.group(1).upper()
            args = match.group(2).strip()

            if action_type == "TERMINAL":
                return f"[TERMINAL OUTPUT]\n{run_command(args)}"
            if action_type == "READ":
                return f"[FILE CONTENT]\n{read_file(args)}"
            if action_type == "WRITE":
                if "|" not in args:
                    return "Error: WRITE expects '<path> | <content>'."
                path, content = args.split("|", 1)
                return write_file(path.strip(), content.strip())
            if action_type == "SEARCH":
                return search_web(args)
            if action_type == "PYTHON":
                return f"[PYTHON RESULT]\n{execute_python(args)}"
            if action_type == "IMAGE":
                return f"[IMAGE URL]\n{generate_image(args)}"
            if action_type == "LIST":
                return "[FILES]\n" + "\n".join(list_project_files(args or "."))
            return f"Unknown action: {action_type}"
        except Exception as e:
            logger.error(f"Execution error: {e}")
            return f"Execution Error: {str(e)}"


class AutonomousOrchestrator:
    def __init__(self):
        self.history = []

    def call_llm(self, prompt, system_msg=None, history=None):
        messages = [{"role": "system", "content": system_msg or PERSONA}]
        for turn in history or []:
            role = turn.get("role", "user")
            content = turn.get("content", "")
            if content:
                messages.append({"role": role, "content": content})
        messages.append({"role": "user", "content": prompt})
        return chat(messages)

    def _recall(self, query):
        """Retrieve relevant long-term memories for RAG context."""
        try:
            memories = memory_instance.query_memory(query, n_results=settings.memory_top_k)
        except Exception as e:  # memory backend optional
            logger.warning(f"Memory recall unavailable: {e}")
            return ""
        if not memories:
            return ""
        return "\n".join(f"- {m}" for m in memories)

    def _make_plan(self, task, recalled):
        prompt = (
            f"TASK: {task}\n"
            f"RELEVANT MEMORY:\n{recalled or '(none)'}\n\n"
            "Draft a concise numbered plan (max 5 steps) to accomplish the task "
            "using the available tools. Reply with the plan only."
        )
        return self.call_llm(prompt, system_msg=PERSONA)

    def _reflect(self, task, context):
        prompt = (
            f"TASK: {task}\n"
            f"PROGRESS SO FAR:\n{context[-2000:]}\n\n"
            "Briefly self-critique (max 3 sentences): are we on track, what was "
            "learned, and what should the next action be?"
        )
        return self.call_llm(prompt, system_msg=ROLE_PROMPTS["analyst"])

    def run_task(self, task, role="general"):
        system_msg = ROLE_PROMPTS.get(role, PERSONA)
        recalled = self._recall(task)

        plan = self._make_plan(task, recalled)
        print(f"\n\033[96m[AI-KU] Target: {task}\033[0m")
        print(f"\033[94m[PLAN]\033[0m\n{plan}\n")

        context = f"PLAN:\n{plan}\n"
        if recalled:
            context += f"\nRELEVANT MEMORY:\n{recalled}\n"

        max_iters = max(1, settings.max_iterations)
        for i in range(max_iters):
            print(f"\033[90m[Iteration {i + 1}/{max_iters}] Thinking...\033[0m", end="\r")

            prompt = (
                f"TASK: {task}\n\nCONTEXT:\n{context}\n\n{ACTION_MENU}"
            )
            response = self.call_llm(prompt, system_msg=system_msg)
            print("\033[K", end="")

            if "FINISH" in response.upper():
                report = response.split("ARGS:", 1)[1].strip() if "ARGS:" in response else response.strip()
                self._remember(f"Task: {task} | Result: {report}")
                return report

            print(f"\033[93m[Action] {response.split('ARGS:')[0].strip()}\033[0m")
            result = ExecutionEngine.execute_action(response)
            if result is None:
                context += f"\n--- Note ---\nNo valid action parsed from: {response[:200]}\n"
                continue

            context += f"\n--- Action Result ---\n{result}\n"

            if settings.enable_reflection and i < max_iters - 1:
                reflection = self._reflect(task, context)
                context += f"\n--- Reflection ---\n{reflection}\n"

        # Out of iterations: ask the model to summarize what it accomplished.
        summary = self.call_llm(
            f"TASK: {task}\n\nWORK LOG:\n{context[-3000:]}\n\n"
            "Iterations exhausted. Provide the best final report you can from the work so far.",
            system_msg=system_msg,
        )
        self._remember(f"Task: {task} | Partial result: {summary}")
        return summary

    @staticmethod
    def _remember(text):
        try:
            memory_instance.add_memory(text)
        except Exception as e:  # memory backend optional
            logger.warning(f"Could not persist memory: {e}")


orchestrator = AutonomousOrchestrator()
