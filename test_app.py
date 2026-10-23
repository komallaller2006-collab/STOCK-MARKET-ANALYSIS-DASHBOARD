from pathlib import Path

import pandas as pd
import importlib.util

project_dir = Path(__file__).resolve().parent
module_name = "nifty_dashboard"
spec = importlib.util.spec_from_file_location(module_name, project_dir / "app.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def test_load_nifty_data_strips_unnamed_index_and_uses_project_csv():
    df = module.load_nifty_data(project_dir / "NIFTY50_with_indicators.csv")

    assert "Unnamed: 0" not in df.columns
    assert "Date" in df.columns
    assert "Close" in df.columns
    assert pd.api.types.is_datetime64_any_dtype(df["Date"])
