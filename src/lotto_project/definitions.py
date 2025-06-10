import dagster as dg
from src.lotto_project.assets.tables_initialization import table_initialization


defs = dg.Definitions(
    assets=[table_initialization]
)
    