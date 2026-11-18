import os
import sys
from pathlib import Path

# Add backend directory to sys.path
backend_path = Path(__file__).resolve().parent / "backend"
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

def classify(text: str) -> dict:
    text_lower = text.lower()
    category = "general"
    for label, words in (
        ("billing", ("refund", "invoice", "payment", "charge")),
        ("technical", ("error", "crash", "bug", "broken")),
        ("account", ("login", "password", "account", "sign in")),
    ):
        if any(word in text_lower for word in words):
            category = label
            break
    urgency = "high" if any(w in text_lower for w in ("urgent", "outage", "immediately")) else "low"
    return {"category": category, "urgency": urgency, "confidence": 0.85}

if __name__ == "__main__":
    import uvicorn
    import importlib.util
    main_path = backend_path / "app" / "main.py"
    spec = importlib.util.spec_from_file_location("main", main_path)
    main_mod = importlib.util.module_from_spec(spec)
    sys.modules["main"] = main_mod
    spec.loader.exec_module(main_mod)
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", "8000"))
    uvicorn.run(main_mod.app, host=host, port=port)
