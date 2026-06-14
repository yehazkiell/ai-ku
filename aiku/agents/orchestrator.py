import g4f
from loguru import logger
from aiku.tools.search import search_web
from aiku.memory.rag import memory_instance
from aiku.agents.registry import AGENT_REGISTRY

class Orchestrator:
    def __init__(self, model_name="ai-ku-omni-godmode"):
        self.model_name = model_name

    def call_llm(self, prompt, role="general", history=[]):
        role_info = AGENT_REGISTRY.get(role, {"prompt": "Anda adalah AI-KU, asisten serba bisa."})
        system_prompt = f"{role_info['prompt']}\n\nYou are operating in the AI-KU GODMODE environment with massive RAG capabilities."

        messages = [{"role": "system", "content": system_prompt}]
        for m in history: messages.append(m)
        messages.append({"role": "user", "content": prompt})

        providers = [
            (g4f.Provider.OperaAria, g4f.models.gpt_4),
            (g4f.Provider.Blackbox, g4f.models.gpt_4),
        ]

        for provider, model in providers:
            try:
                logger.info(f"LLM Call: {provider.__name__}")
                return g4f.ChatCompletion.create(model=model, provider=provider, messages=messages)
            except Exception as e:
                logger.warning(f"Provider {provider.__name__} error: {e}")
                continue
        return "Error: All providers failed."

    def run_multi_agent_task(self, user_prompt):
        logger.info(f"Orchestrating task: {user_prompt}")

        # 1. RETRIEVE (RAG)
        relevant_mems = memory_instance.query_memory(user_prompt)
        rag_context = "\n[MEMORI LOKAL TERKAIT]:\n" + ("\n".join(relevant_mems) if relevant_mems else "Tidak ada memori terkait.")

        # 2. RESEARCH (Search)
        print("\033[90m[Agent: Researcher] Browsing for information...\033[0m")
        search_data = search_web(user_prompt)

        # 3. PLAN & ANALYZE (Analyst)
        print("\033[90m[Agent: Analyst] Reasoning and planning...\033[0m")
        analyst_prompt = f"TASK: {user_prompt}\n{rag_context}\n{search_data}\n\nLakukan analisis data di atas dan buatkan draf solusi teknis."
        analysis = self.call_llm(analyst_prompt, role="analyst")

        # 4. EXECUTE & FINALIZE (Lead)
        print("\033[90m[Agent: Lead] Finalizing professional response...\033[0m")
        final_prompt = f"USER REQUEST: {user_prompt}\nANALYSIS: {analysis}\n\nBerdasarkan riset dan analisis tim, berikan jawaban final terbaik."
        final_response = self.call_llm(final_prompt, role="lead")

        # Auto-save to memory
        memory_instance.add_memory(f"User Task: {user_prompt} | AI Solution: {final_response[:1000]}")

        return final_response

orchestrator = Orchestrator()
