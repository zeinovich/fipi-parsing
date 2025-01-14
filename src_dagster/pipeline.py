from dagster import job, schedule, repository
from operations import extract_op, transform_load_op

# Define the job
@job
def fipi_job():
    db_path = extract_op()
    transform_load_op(db_path)

# Define the schedule
@schedule(cron_schedule="0 9 * * *", job=fipi_job, execution_timezone="UTC")
def daily_schedule(context):
    return {
        "ops": {
            "extract_op": {
                "config": {
                    "db_path": "artifacts/tasks.db"
                }
            },
            "transform_load_op": {
                "config": {
                    "db_path": "artifacts/tasks.db",
                    "chroma_dir": "./chroma"
                }
            }
        }
    }

# Define the repository
@repository
def fipi_repository():
    return [fipi_job, daily_schedule]