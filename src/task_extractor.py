from typing import List, Optional

from pydantic import BaseModel
from bs4 import BeautifulSoup
from bs4.element import PageElement

from src.constants import MULTI_CHOICE_TASK_TYPE
from src.multi_choice_solver import solve_multi_choice_task


class Task(BaseModel):
    id: str
    guid: str
    task_info: str
    content: str
    answer: Optional[str]
    answer_type: str
    tags: List[str]


class TaskExtractor:
    def __init__(self, html_content: str):
        self.html_content = html_content
        self.soup = BeautifulSoup(self.html_content, "html.parser")

    def extract_tasks(self):
        tasks = self.soup.find_all("div", {"class": "qblock"})
        return tasks

    def extract_task(self, task: PageElement):
        task_id = task.get("id", None)

        if task_id is None:
            return None

        task_info = f"i{task_id[1:]}"
        task_guid = task.find("input", {"name": "guid"})["value"]
        task_content = ""
        task_contents = task.find_all("p")

        for i, elem in enumerate(task_contents):
            if i != len(task_contents) - 1:
                task_content = task_content.strip()
                task_content += "\n"
            task_content += elem.text

        info = self.soup.find("div", {"id": task_info})
        tags = []

        for td in info.find_all("td", {"class": "param-row"}):
            tags.append(td.text)

        answer_type = info.find_all("td")[-1].text
        answer = ""

        # if answer_type == MULTI_CHOICE_TASK_TYPE:
        #     answer = solve_multi_choice_task(task_guid)

        return Task(
            id=task_id,
            guid=task_guid,
            task_info=task_info,
            content=task_content,
            answer=answer,
            answer_type=answer_type,
            tags=tags,
        )
