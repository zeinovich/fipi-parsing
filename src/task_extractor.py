from bs4 import BeautifulSoup
from pydantic import BaseModel
from typing import List
from bs4.element import PageElement

class Task(BaseModel):
    id: str
    guid: str
    task_info: str
    content: str
    answer: str
    answer_type: str
    tags: List[str]

class TaskExtractor:
    def __init__(self, html_content: str):
        self.html_content = html_content
        self.soup = BeautifulSoup(self.html_content, 'html.parser')

    def extract_tasks(self):
        tasks = self.soup.find_all('div', {'class': 'qblock'})
        return tasks
    
    def extract_task(self, task: PageElement):
        task_id = task['id']
        task_info = f'i{task_id[1:]}'
        task_guid = task.find('input', {'name': 'guid'})['value']
        task_content = ""
        task_contents = task.find_all('p')
        for i, elem in enumerate(task_contents):
            if i != len(task_contents) - 1:
                task_content = task_content.strip()
                task_content += "\n"
            task_content += elem.text
        info = self.soup.find('div', {'id': task_info})
        tags = []
        for td in info.find_all('td', {'class': 'param-row'}):
            tags.append(td.text)
        answer = ""
        answer_type = info.find_all('td')[-1].text
        return Task(id=task_id, guid=task_guid, task_info=task_info, content=task_content, answer=answer, answer_type=answer_type, tags=tags)
