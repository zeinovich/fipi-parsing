import requests
from src.constants import QUESTIONS_URL, PAGES_COUNT
from src.task_extractor import TaskExtractor

def main():
    for page in range(1, PAGES_COUNT + 1):
        page_content = process_page(page)
        parse_page(page_content)

def process_page(page: int):
    url = QUESTIONS_URL + f"&page={page}"
    response = requests.get(url)
    return response.text

def parse_page(page_content: str):
    extractor = TaskExtractor(page_content)
    tasks = extractor.extract_tasks()
    for task in tasks:
        task_data = extractor.extract_task(task)
        print(f'=== NEW TASK ===')
        print(f'id: {task_data.id}')
        print(f'guid: {task_data.guid}')
        print(f'task_info: {task_data.task_info}')
        print(f'content: {task_data.content}')
        print(f'answer: {task_data.answer}')
        print(f'answer_type: {task_data.answer_type}')
        print(f'tags: {task_data.tags}')
        print(f'=== END OF TASK ===')

if __name__ == "__main__":
    main()

