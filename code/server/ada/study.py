"""The module for storing the study data for each participant.

```json
{
    "current_stage": main_task, # main_task, pre_task, post_task, None
    "tasks": [
        {
            "task_id": "pre_task",
            "complete": true,
        },
        {
            "task_id": "task_2",
            "style": "considerate",
            "complete": true,
        },
        {
            "task_id": "task_3",
            "style": "involved",
            "complete": false,
        },
        {
            "task_id": "task_1",
            "style": "agent_choice",
            "complete": false,
        }
    ]
}
```
"""
import json
import random
from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional, Tuple

_DEFAULT_STUDY_PATH = "export/study/{study_id}.json"


@dataclass
class Task:
    task_id: str
    complete: bool = False
    style: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    conversation: Optional[List[Dict[str, Any]]] = None


@dataclass
class Study:
    study_id: str
    current_stage: str
    tasks: List[Task]


class StudyTracker:
    def __init__(self, study_id: str, path: Optional[str] = None) -> None:
        """Study."""
        self._path = path or _DEFAULT_STUDY_PATH.format(study_id=study_id)
        self._study = self.load_study() or self.generate_new_study(study_id)

    def get_current_stage(self) -> Tuple[Optional[str], Optional[str]]:
        """Gets the current task and stage."""
        current_task = next(
            task.task_id for task in self._study.tasks if not task.complete
        )
        current_stage = self._study.current_stage
        return current_task, current_stage

    def generate_new_study(self, study_id: str) -> Study:
        """Generates a new study with randomized tasks and styles."""
        styles = ["considerate", "involved"]
        tasks = ["task_1", "task_2", "task_3"]

        # Randomize the task order
        random.shuffle(tasks)
        random.shuffle(styles)
        styles.append("user_agency")

        # Create Task instances with randomized styles
        task_instances = [
            Task(task_id=task_id, style=style)
            for task_id, style in zip(tasks, styles)
        ]

        # Create a new Study instance
        new_study = Study(
            study_id=study_id,
            current_stage="pre_task",
            tasks=task_instances,
        )

        # Optionally, you can save the new study right away
        self.save_study(new_study)

        return new_study

    def load_study(self) -> Optional[Study]:
        """Loads the study from a JSON file."""
        try:
            with open(self._path, "r") as file:
                data = json.load(file)
                tasks = [Task(**task) for task in data.get("tasks", [])]
                return Study(
                    study_id=data["study_id"],
                    current_stage=data.get("current_stage", None),
                    tasks=tasks,
                )
        except (FileNotFoundError, json.JSONDecodeError):
            # Return a default Study instance if file doesn't exist or is empty
            return None

    def save_study(self, study: Study) -> None:
        """Saves the study to a JSON file."""
        with open(self._path, "w") as file:
            # Convert Study instance to a dictionary and then to JSON
            study_dict = asdict(study)
            study_dict["tasks"] = [asdict(task) for task in study.tasks]
            json.dump(study_dict, file, indent=4)
