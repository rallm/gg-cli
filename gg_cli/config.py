import json
import os
import sys
from pathlib import Path
from typing import Any, Dict
from gg_cli.git_ops import GitOps

class ConfigManager:
    DEFAULT_CONFIG = {
        "profile": {
            "name": "",
            "email": ""
        },
        "push_confirmation": False,
        "version": "0.0.0",
        "main_branch": "main",
        "develop_branch": "develop"
    }

    def __init__(self):
        if not GitOps.is_git_repo():
            print("[ERROR] Not inside a Git repository. Run 'git init' first.", file=sys.stderr)
            sys.exit(1)
        
        self.repo_root = Path(GitOps.get_repo_root())
        self.config_dir = self.repo_root / ".git" / "gg"
        self.config_file = self.config_dir / "config.json"

    def init_config(self) -> None:
        if not self.config_dir.exists():
            self.config_dir.mkdir(parents=True, exist_ok=True)
        if not self.config_file.exists():
            self.save(self.DEFAULT_CONFIG)

    def load(self) -> Dict[str, Any]:
        if not self.config_file.exists():
            print("[ERROR] gg is not initialized in this repo. Run 'gg init' first.", file=sys.stderr)
            sys.exit(1)
        with open(self.config_file, "r", encoding="utf-8") as f:
            return json.load(f)

    def save(self, data: Dict[str, Any]) -> None:
        if not self.config_dir.exists():
            self.config_dir.mkdir(parents=True, exist_ok=True)
        with open(self.config_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    def get(self, key: str) -> Any:
        data = self.load()
        return data.get(key)

    def update(self, key: str, value: Any) -> None:
        data = self.load()
        data[key] = value
        self.save(data)