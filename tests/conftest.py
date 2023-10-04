import asyncio
from pathlib import Path

import pytest

from src.common import Paths
from src.common import create_dataclass_factory



@pytest.fixture(scope="session")
def paths():
    paths = Paths(Path(__file__).parent)
    return paths


@pytest.fixture(scope="session")
def event_loop():
    try:
        return asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop


@pytest.fixture(scope="session")
def dcf():
    return create_dataclass_factory()
