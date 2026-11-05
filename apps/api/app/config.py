from pathlib import Path
import os


DATA_DIR = Path(os.getenv("DATA_DIR", "data")).resolve()
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/ai_data_analyst.db")
MAX_UPLOAD_BYTES = int(os.getenv("MAX_UPLOAD_BYTES", str(100 * 1024 * 1024)))
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen3.5:9b")
