import requests
import json

from tqdm import tqdm

from src.constants import QUESTIONS_URL, PAGES_COUNT
from src.task_extractor import TaskExtractor


def main():
    tasks = []

    for page in tqdm(range(1, PAGES_COUNT + 1)):
        page_content = process_page(page)
        page_tasks = parse_page(page_content)

        tasks.extend(page_tasks)

    with open("./data/raw/tasks.json", "w") as f:
        json.dump(
            tasks,
            f,
            indent=4,
            ensure_ascii=False,
        )


def process_page(page: int):
    url = QUESTIONS_URL + f"&page={page}"
    response = requests.get(url)
    return response.text


def parse_page(page_content: str):
    extractor = TaskExtractor(page_content)
    tasks = extractor.extract_tasks()
    task_list = []

    for task in tasks:
        task_data = extractor.extract_task(task)

        if task_data is None:
            print("Task can't be extracted")
            continue

        task_list.append(task_data.model_dump())

    return task_list


if __name__ == "__main__":
    main()
