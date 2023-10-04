from typing import List, Optional
from fastapi import HTTPException, UploadFile
import pandas as pd
from io import StringIO

import os
from src.api.dependencies.file import file_provider


uploaded_files = []


async def upload_file_service(
        file: UploadFile, 
        file_provider: file_provider
):
    content = await file.read()
    with open(file_provider.path / file.filename, "wb") as f:
        f.write(content)
    content = StringIO(content.decode('utf-8'))
    df = pd.read_csv(content)
    file_data = {"filename": file.filename, "columns": df.columns.tolist()}
    return file_data



async def get_files_service(file_provider: file_provider):
    files_list = []
    for file in os.listdir(file_provider.path):
        with open(file_provider.path / file, "rb") as f:
            content = f.read()
        content = StringIO(content.decode('utf-8'))
        df = pd.read_csv(content)
        file_data = {"filename": file, "columns": df.columns.tolist()}
        files_list.append(file_data)
    return files_list


async def get_file_data_service(
        file_name: str, 
        file_provider: file_provider,
        filters: Optional[str], 
        sort_by: Optional[List[str]],
        ascending: bool = True,
):
    try:
        with open(file_provider.path / file_name, "rb") as f:
            content = f.read()
        content = StringIO(content.decode('utf-8'))
        df = pd.read_csv(content)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Файл не найден")
    if filters:
        filters = eval(filters)
        for column, values in filters.items():
            df = df[df[column].isin(values)]    
    if sort_by:
        df = df.sort_values(by=sort_by, ascending=ascending)
    return df.to_dict(orient='records')