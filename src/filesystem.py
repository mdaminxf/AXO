import os
import shutil
from pathlib import Path

class FileSystemManager:
    def __init__(self, shared_dir="shared"):
        self.shared_dir = Path(shared_dir)
        self.shared_dir.mkdir(exist_ok=True)
        self.permissions = {} # path -> [users]

    def is_allowed(self, path, user):
        # Basic check: only allow files inside shared_dir
        abs_path = Path(path).resolve()
        abs_shared = self.shared_dir.resolve()
        
        if not str(abs_path).startswith(str(abs_shared)):
            return False
        
        # Additional permission check can be added here
        return True

    def list_files(self):
        return [str(p.relative_to(self.shared_dir)) for p in self.shared_dir.rglob("*") if p.is_file()]

    def get_file_content(self, relative_path):
        target = self.shared_dir / relative_path
        if self.is_allowed(target, "anyone"): # Simplified for MVP
            with open(target, "rb") as f:
                return f.read()
        return None

    def save_file(self, relative_path, content):
        target = self.shared_dir / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        with open(target, "wb") as f:
            f.write(content)
        return True
