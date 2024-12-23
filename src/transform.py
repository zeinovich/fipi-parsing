import json
import sqlite3
from tqdm import tqdm
from typing import List, Dict

from chromadb import PersistentClient
from sentence_transformers import SentenceTransformer

from src.utils import logger

DEFAULT_DB_PATH = "artifacts/tasks.db"
DEFAULT_CHROMA_DIR = "./chroma"


def transform_load(db_path: str, chroma_dir: str = None):
    logger.info(f"[TRANSFORM & LOAD] DB: {db_path}")
    logger.info(f"[TRANSFORM & LOAD] Chroma: {chroma_dir}")

    try:
        tasks = _load_tasks(db_path)
        _tl_embeddings(tasks, chroma_dir)
    except Exception as e:
        logger.error(e)
        raise e


def _tl_embeddings(tasks: List[Dict[str, str]], chroma_dir: str = DEFAULT_CHROMA_DIR):
    # Initialize Chroma client
    client = PersistentClient(path=chroma_dir)

    # Create a collection
    tasks_collection = client.create_collection(name="tasks")
    options_collection = client.create_collection(name="options")

    logger.info(f"Initialized Chroma DB (persistent) at {chroma_dir}")

    model = SentenceTransformer("sergeyzh/rubert-tiny-turbo")

    # Transform tasks into embeddings (example transformation)
    for task in tqdm(tasks):
        id_, task_text, options = task.values()
        e_task = model.encode(task_text, show_progress_bar=False)
        e_options = model.encode(options, show_progress_bar=False)

        tasks_collection.add(
            embeddings=[e_task],
            documents=[json.dumps(task, ensure_ascii=False)],
            metadatas=[{"source": "web"}],
            ids=id_,
        )
        options_collection.add(
            embeddings=[e_options],
            documents=[json.dumps(task, ensure_ascii=False)],
            metadatas=[{"source": "web"}],
            ids=id_,
        )

    logger.info(f"Processed {len(tasks)} documents and dumped to Chroma")
    client.clear_system_cache()


def _load_tasks(db_path: str = DEFAULT_DB_PATH) -> List[Dict[str, str]]:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Query to count the total number of tasks
    cursor.execute(
        """
        SELECT json_group_array(
            json_object(
                'id', id, 
                'task_text', task_text, 
                'options', options
                )
        )
        FROM tasks
        """
    )
    tasks = cursor.fetchall()[0][0]

    conn.close()

    tasks = json.loads(tasks)
    logger.info(f"Loaded {len(tasks)} tasks from SQL DB")

    return tasks


if __name__ == "__main__":
    transform(DEFAULT_DB_PATH, DEFAULT_CHROMA_DIR)
