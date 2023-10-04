from fastapi import APIRouter

from src.api.routes import file_operation
from src.api.routes import user

def setup(router: APIRouter):
    file_operation.setup(router)
    user.setup(router)