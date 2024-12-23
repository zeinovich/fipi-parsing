import requests
import json
import sqlite3

from typing import List

from tqdm import tqdm

from src.constants import QUESTIONS_URL, PAGES_COUNT
from src.task_extractor import TaskExtractor, Task

from src.utils import logger

DEFAULT_DB_PATH = "artifacts/tasks.db"


def extract(db_path: str):
    for page in tqdm(range(1, PAGES_COUNT + 1)):
        try:
            page_content = process_page(page)
            page_tasks = parse_page(page_content)

            load_into_sqlite(page_tasks, db_path)
        except Exception as e:
            logger.error(e)

    logger.info(f"Extracted {get_total_tasks(db_path)} tasks")
    


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
            logger.warning("Task can't be extracted")
            continue

        task_list.append(task_data)

    return task_list


def load_into_sqlite(tasks: List[Task], db_path: str):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create table if not exists
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS tasks (
            id TEXT PRIMARY KEY,
            guid TEXT,
            task_info TEXT,
            task_text TEXT,
            options TEXT,
            answer TEXT,
            answer_type TEXT,
            tags TEXT
        )
    """
    )

    # Insert tasks into the table
    for task in tasks:
        task = task.model_dump()
        
        cursor.execute(
            """
            INSERT OR REPLACE INTO tasks (id, guid, task_info, task_text, options, answer, answer_type, tags)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                task["id"],
                task["guid"],
                task["task_info"],
                task["task_text"],
                task["options"],
                task.get("answer", None),
                task["answer_type"],
                json.dumps(task["tags"], ensure_ascii=False)[0],
            ),
        )

    conn.commit()
    conn.close()


def get_total_tasks(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Query to count the total number of tasks
    cursor.execute("SELECT COUNT(*) FROM tasks")
    total_tasks = cursor.fetchone()[0]

    conn.close()

    return total_tasks


if __name__ == "__main__":
    extract(DEFAULT_DB_PATH)
