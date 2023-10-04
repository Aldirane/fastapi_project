from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from src.infrastructure.db.config.models.db import DBConfig
from .paths import Paths


@dataclass
class Config:
    paths: Paths
    db: DBConfig
    file_storage_config: FileStorageConfig

    @property
    def app_dir(self) -> Path:
        return self.paths.app_dir

    @property
    def config_path(self) -> Path:
        return self.paths.config_path


@dataclass
class FileStorageConfig:
    path: Path
