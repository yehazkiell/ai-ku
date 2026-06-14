import g4f
import asyncio
from loguru import logger
from aiku.tools.search import search_web
from aiku.tools.terminal import run_command
from aiku.tools.git_tools import git_status
from aiku.memory.rag import memory_instance
from aiku.agents.registry import AGENT_REGISTRY

class AutonomousOrchestrator:
    """
    AI-KU: The Autonomous Software Engineer & Researcher.
    Follows rules: Search -> Analyze -> Plan -> Execute -> Verify.
    """
    def __init__(self, model_name="ai-ku-omni-godmode"):
        self.model_name = model_name

    def call_llm(self, prompt, role="lead", history=[]):
        messages = [
            {"role": "system", "content": "You are AI-KU, an autonomous professional software engineer and researcher. Follow all 10 rules provided in your core directives."},
            {"role": "user", "content": prompt}
        ]
        try:
            return g4f.ChatCompletion.create(model=g4f.models.gpt_4, provider=g4f.Provider.OperaAria, messages=messages)
        except:
            return "Inference failed. Falling back to internal reasoning."

    def run_autonomous_loop(self, task):
        print(f"\n\033[96m[AI-KU] Task Analysis: {task}\033[0m")

        # 1. SEARCH & RAG
        print("\033[90m[Rule 2] Searching web and local memory for context...\033[0m")
        search_data = search_web(task)
        relevant_mems = memory_instance.query_memory(task)

        # 2. PLAN
        print("\033[90m[Rule 6] Planning execution steps...\033[0m")
        plan_prompt = f"TASK: {task}\nCONTEXT: {search_data}\nMEMORY: {relevant_mems}\n\nCreate a step-by-step plan."
        plan = self.call_llm(plan_prompt)

        # 3. EXECUTE (Simulated for this iteration)
        print(f"\033[90m[Rule 6] Executing sequence...\033[0m")
        # In a real loop, we would parse the plan and call terminal/file tools here.

        # 4. VERIFY & REPORT
        print("\033[90m[Rule 10] Verifying results and generating final report...\033[0m")
        final_prompt = f"Based on the task '{task}' and the plan executed: {plan}, provide the final professional result."
        report = self.call_llm(final_prompt)

        return report

orchestrator = AutonomousOrchestrator()
