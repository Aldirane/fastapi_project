import uvicorn as uvicorn
from fastapi import FastAPI

from src.api import dependencies, routes
from src.api.config.parser.main import load_config
from src.api.main_factory import (
    get_paths,
    create_app,
)
from src.infrastructure.db.factory import create_pool


def main() -> FastAPI:
    paths = get_paths()
    config = load_config(paths)
    app = create_app()
    pool = create_pool(config.db)
    dependencies.setup(app=app, pool=pool, config=config)
    routes.setup(app.router)
    return app


def run():
    uvicorn.run("src.api:main", factory=True, reload= True)


if __name__ == "__main__":
    run()