import io
import pytest
import pytest_asyncio
from httpx import AsyncClient
import pandas as pd

@pytest_asyncio.fixture
async def file_data():
    file = "cats_vs_dogs.csv"
    data = open("tests/fixtures/resources/"+file, "rb").read()
    return (file, data)


@pytest.mark.asyncio
async def test_file_upload(client: AsyncClient, file_data):
    resp = await client.post(
        "/file/upload",
        files={"file":file_data},
        follow_redirects = True,
    )
    assert resp.is_success


@pytest.mark.asyncio
async def test_get_files(client: AsyncClient, file_data):
    resp = await client.get(
        "/files",
        follow_redirects = True,
    )
    assert resp.is_success
    content = resp.json()[0]
    file = file_data[1]
    file = io.StringIO(file.decode('utf-8'))
    df = pd.read_csv(file)
    assert df.columns.to_list() == content["columns"]


@pytest.mark.asyncio
async def test_get_file(client: AsyncClient, file_data):
    filters = {"state": ["Alabama"]}
    resp = await client.get(
        f"/file/{file_data[0]}",
        params={'filters': filters},
        follow_redirects = True,
    )
    assert resp.is_success
    content = resp.json()[0]
    file = file_data[1]
    file = io.StringIO(file.decode('utf-8'))
    df = pd.read_csv(file)
    df = df[df["state"].isin(filters["state"])] 
    assert df.to_dict(orient="records")[0] == content

