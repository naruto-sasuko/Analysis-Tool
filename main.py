import os
import subprocess
import sys
from pathlib import Path

# Ensure UTF-8 output on Windows consoles
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


def main():
    """Launcher for the Analysis Tool Streamlit web application."""
    base_dir = Path(__file__).resolve().parent
    app_file = base_dir / "app.py"
    if not app_file.exists():
        app_file = base_dir / "Analysis tool.py"

    print(f"⚡ Launching Analysis Tool: {app_file}")
    cmd = [sys.executable, "-X", "utf8", "-m", "streamlit", "run", str(app_file)]
    try:
        subprocess.run(cmd)

    except KeyboardInterrupt:
        print("\nAnalysis Tool stopped.")


if __name__ == "__main__":
    main()
