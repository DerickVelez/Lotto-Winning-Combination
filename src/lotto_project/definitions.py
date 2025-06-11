import dagster as dg
from src.lotto_project.assets.tables_initialization import table_initialization
from src.lotto_project.assets.lotto_result import get_current_lotto_result, get_monthly_lotto_result
from src.lotto_project.assets.gemini import get_monthly_lotto_result_gemini



defs = dg.Definitions(
    assets=[table_initialization, get_current_lotto_result,get_monthly_lotto_result, get_monthly_lotto_result_gemini]
)
    