import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from app import create_app

app = create_app()

if __name__ == "__main__":
    errors = app.config["CONFIG_ERRORS"] if "CONFIG_ERRORS" in app.config else []
    if errors:
        for err in errors:
            print(f"KONFIGURASI ERROR: {err}", file=sys.stderr)
        sys.exit(1)
    app.run(debug=True, host="127.0.0.1", port=5000)