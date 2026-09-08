"""
Entry point for the Analysis Tool Streamlit web application.
Enables execution without whitespace in the script filename:
    streamlit run app.py
"""
import sys
from pathlib import Path
import runpy

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

app_file = Path(__file__).resolve().parent / "Analysis tool.py"

if __name__ == "__main__" or __name__.startswith("streamlit"):
    runpy.run_path(str(app_file), run_name="__main__")
