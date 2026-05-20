import os
import yaml
from typing import Any, Dict

class Config:
    def __init__(self, config_path: str = "config.yaml"):
        self.config: Dict[str, Any] = {}
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                self.config = yaml.safe_load(f)

    def get(self, key: str, default: Any = None) -> Any:
        # Check env first
        env_key = f"STRATUM_{key.upper()}"
        if env_key in os.environ:
            return os.environ[env_key]

        # Check config file
        keys = key.split('.')
        val = self.config
        for k in keys:
            if isinstance(val, dict):
                val = val.get(k)
            else:
                val = None
                break

        return val if val is not None else default

# Global config instance
config = Config()
