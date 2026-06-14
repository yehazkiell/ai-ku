import os
import json
from core import get_ai_response, search_web, execute_python

class ManusEngine:
    """
    Manus AI Engine: General Purpose Agent for 'Hand-on' task execution.
    Focuses on multi-step skill acquisition and complex problem solving.
    """
    def __init__(self):
        self.skills_file = 'manus/skills.json'
        self.load_skills()

    def load_skills(self):
        if os.path.exists(self.skills_file):
            with open(self.skills_file, 'r') as f:
                self.skills = json.load(f)
        else:
            self.skills = {
                "web_navigation": "Advanced",
                "data_synthesis": "Expert",
                "code_generation": "Godmode",
                "autonomous_learning": "Active"
            }
            self.save_skills()

    def save_skills(self):
        with open(self.skills_file, 'w') as f:
            json.dump(self.skills, f, indent=4)

    def upgrade_skill(self, skill_name, level):
        self.skills[skill_name] = level
        self.save_skills()
        return f"Skill '{skill_name}' upgraded to {level}."

    def execute_general_task(self, task):
        print(f"\033[94m[Manus AI] Analyzing task: {task}\033[0m")
        # Simulate multi-step 'Hands-on' execution
        context = f"Manus Skills: {json.dumps(self.skills)}\n"

        # Step 1: Browse/Research
        data = search_web(task)

        # Step 2: Formulate solution
        prompt = f"You are Manus AI, a general-purpose agent. Using your skills {self.skills}, solve: {task}\nData: {data}"
        response = get_ai_response(prompt, model='ai-ku-omni-godmode')

        return response

manus_instance = ManusEngine()
