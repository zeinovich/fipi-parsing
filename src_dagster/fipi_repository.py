from pipeline import fipi_repository

if __name__ == "__main__":
    from dagster import execute_pipeline
    result = execute_pipeline(fipi_repository.get_pipeline("fipi_job"))
    assert result.success
