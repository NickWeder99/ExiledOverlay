import json
import os

class LevelGuide:
    def __init__(self):
        self.guide_texts = {}
        self._load_guide_texts()

    def _load_guide_texts(self):
        try:
            file_path = os.path.join(os.path.dirname(__file__), "../../data/levelguide.json")
            with open(file_path, "r", encoding="utf-8") as f:
                self.guide_texts = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading level guide JSON: {e}")
            self.guide_texts = {"Act 1": ["No guide data available."]}

    def get_acts(self):
        if self.guide_texts:
            # Extract the numeric part and sort by that
            def act_key(act_name):
                # Extract number after "Act "
                try:
                    return int(act_name.split(" ")[1])
                except (IndexError, ValueError):
                    return float('inf')  # put malformed entries at the end

            return sorted(self.guide_texts.keys(), key=act_key)
        else:
            return [f"Act {i}" for i in range(1, 11)]


    def get_tasks_for_act(self, act):
        # Returns the list of tasks for the given act or an empty list if none
        tasks = self.guide_texts.get(act)
        if isinstance(tasks, list):
            return tasks
        else:
            return []
