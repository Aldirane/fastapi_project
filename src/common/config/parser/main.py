import os
from pathlib import Path
from dataclass_factory import Factory

from src.common.config.models.main import Config, FileStorageConfig
from src.common.config.models.paths import Paths
from src.infrastructure.db.config.parser.db import load_db_config


def load_config(config_dct: dict, paths: Paths, dcf: Factory) -> Config:
    return Config(
        paths=paths,
        db=load_db_config(config_dct["db"]),
        file_storage_config=load_file_storage_config(paths, config_dct["file-storage-config"], dcf),
    )


def load_file_storage_config(paths: Paths, config_dct: dict, dcf: Factory) -> FileStorageConfig:
    config_dct["path"]: Path = paths.app_dir / config_dct["path"]
    if not os.path.exists(config_dct["path"]):
        os.makedirs(config_dct["path"])
    return dcf.load(config_dct, FileStorageConfig)
