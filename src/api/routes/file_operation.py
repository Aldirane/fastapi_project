from typing import List, Optional
from fastapi import APIRouter, Depends
from fastapi import UploadFile, File, Query

from src.api.dependencies import file_provider
from src.core.services.file_operation import get_file_data_service, get_files_service, upload_file_service

uploaded_files = []


async def upload_file(
        file: UploadFile = File(...),
        file_provider = Depends(file_provider),
):
    file_data = await upload_file_service(file, file_provider)
    return file_data


async def get_files(file_provider = Depends(file_provider)):
    files_list = await get_files_service(file_provider)
    return files_list


async def get_data(
        file_name: str, 
        file_provider = Depends(file_provider),
        filters: Optional[str] = None, 
        sort_by: Optional[List[str]] = Query(None),
        ascending: bool = True,
):
    data_file = await get_file_data_service(file_name, file_provider, filters, sort_by, ascending)
    return data_file


def setup(router: APIRouter):
    router.add_api_route("/file/upload", upload_file, methods=["POST"])
    router.add_api_route("/files", get_files, methods=["GET"])
    router.add_api_route("/file/{file_name}", get_data, methods=["GET"])