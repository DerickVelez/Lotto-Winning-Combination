from dagster import asset
from src.lotto_project.models.databasemanager import Base, engine


@asset
def table_initialization():
    Base.metadata.create_all(engine)
    return " Tables created."

@asset
def bronze_lotto_result():
    return "hello_world"    