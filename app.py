from pathlib import Path
import runpy

PROJECT_APP = (
    Path(__file__).resolve().parent
    / "Customer Churn Retention Analysis Project"
    / "app.py"
)

runpy.run_path(str(PROJECT_APP), run_name="__main__")
