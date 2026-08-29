import os
import logging
from app.core.config import settings

logger = logging.getLogger("varisetu.storage")


class StorageAdapter:
    """File storage interface (Local disk / Supabase Storage)."""
    def __init__(self):
        self.provider = settings.STORAGE_PROVIDER
        self.upload_dir = settings.STORAGE_LOCAL_DIR
        os.makedirs(self.upload_dir, exist_ok=True)

    async def save_file(self, filename: str, content: bytes) -> str:
        filepath = os.path.join(self.upload_dir, filename)
        with open(filepath, "wb") as f:
            f.write(content)
        return f"/uploads/{filename}"

    async def delete_file(self, filename: str) -> bool:
        filepath = os.path.join(self.upload_dir, filename)
        if os.path.exists(filepath):
            os.remove(filepath)
            return True
        return False


storage_adapter = StorageAdapter()
