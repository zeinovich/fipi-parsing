# from dagster import pipeline, solid, Field, String, schedule, repository

# # Import the functions from your modules
# from src.extract import extract
# from src.transform import transform_load


# # Define solids for each step in the pipeline
# @solid(config_schema={"db_path": Field(String, description="DB path (sqlite3)")})
# def extract_solid(context):
#     db_path = context.solid_config["db_path"]
#     extract(db_path)


# @solid(config_schema={"db_path": Field(String, description="DB path (sqlite3)"),
#                       "chroma_dir": Field(String, description="Chroma persistent directory")})
# def transform_load_solid(context):
#     db_path = context.solid_config["db_path"]
#     chroma_dir = context.solid_config["chroma_dir"]
#     transform_load(db_path, chroma_dir)

# # Define the pipeline
# @pipeline
# def fipi_pipeline():
#     extract_result = extract_solid.alias("extract")()
#     transform_load_solid.alias("transform_load")()

# # Define the schedule
# @schedule(cron_schedule="15 * * * *", pipeline_name="fipi_pipeline", execution_timezone="UTC")
# def daily_schedule(context):
#     return {
#         "solids": {
#             "extract": {
#                 "config": {
#                     "db_path": "artifacts/tasks.db"
#                 }
#             },
#             "transform_load": {
#                 "config": {
#                     "db_path": "artifacts/tasks.db",
#                     "chroma_dir": "./chroma"
#                 }
#             }
#         }
#     }

# # Define the repository
# @repository
# def fipi_repository():
#     return [fipi_pipeline, daily_schedule]


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