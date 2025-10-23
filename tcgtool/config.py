"""Configuration management for the TCG tool."""

import os
import yaml
from pathlib import Path
from dotenv import load_dotenv
from typing import Dict, Any

# Load environment variables
load_dotenv()


class Config:
    """Application configuration."""

    def __init__(self, config_path: str = "config.yaml"):
        """Initialize configuration.

        Args:
            config_path: Path to the YAML configuration file
        """
        self.config_path = Path(config_path)
        self._config: Dict[str, Any] = {}
        self.load()

    def load(self):
        """Load configuration from YAML file."""
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                self._config = yaml.safe_load(f) or {}
        else:
            self._config = self._default_config()

    def _default_config(self) -> Dict[str, Any]:
        """Return default configuration."""
        return {
            'database': {'path': 'data/tcgtool.db'},
            'export': {'output_directory': 'exports'},
            'cache': {'directory': 'data/cache'},
            'logging': {'level': 'INFO'}
        }

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value.

        Args:
            key: Configuration key (supports dot notation, e.g., 'database.path')
            default: Default value if key not found

        Returns:
            Configuration value
        """
        keys = key.split('.')
        value = self._config

        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default

            if value is None:
                return default

        return value

    @property
    def pokemon_tcg_api_key(self) -> str:
        """Get Pokemon TCG API key from environment or config."""
        return os.getenv('POKEMON_TCG_API_KEY', '') or self.get('api_keys.pokemon_tcg_api', '')

    @property
    def database_path(self) -> Path:
        """Get database path."""
        return Path(self.get('database.path', 'data/tcgtool.db'))

    @property
    def export_directory(self) -> Path:
        """Get export directory."""
        return Path(self.get('export.output_directory', 'exports'))


# Global configuration instance
config = Config()
