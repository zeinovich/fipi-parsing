from dagster import op, Output, Field, String
from src.extract import extract
from src.transform import transform_load

# Define operations for each step in the pipeline
@op(config_schema={"db_path": Field(String, description="DB path (sqlite3)")})
def extract_op(context):
    db_path = context.op_config["db_path"]
    extract(db_path)
    return Output(value=db_path)

@op(config_schema={"db_path": Field(String, description="DB path (sqlite3)"),
                   "chroma_dir": Field(String, description="Chroma persistent directory")})
def transform_load_op(context, db_path):
    db_path = context.op_config["db_path"]
    chroma_dir = context.op_config["chroma_dir"]
    transform_load(db_path, chroma_dir)
    return Output(value=chroma_dir)
