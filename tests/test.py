import argparse
import io
import json
import logging
from pathlib import Path
from zipfile import ZipFile

import pytest
from flask.testing import FlaskClient

from hls_job_server.main import build_app, get_tools

DIR_CURRENT = Path(__file__).parent


@pytest.fixture
def client() -> FlaskClient:
    parser = argparse.ArgumentParser(description="HLS Job Server")
    parser.add_argument("--port", type=int, default=5000, help="Port to listen on")
    parser.parse_args([])
    app = build_app()
    app.logger.setLevel(logging.DEBUG)
    # app.config.update({"TESTING": True})
    return app.test_client()


@pytest.fixture
def test_proj_vitis() -> io.BytesIO:
    dir_proj = DIR_CURRENT / "test_proj_vitis"
    zip_proj_bytes = io.BytesIO()
    zip_proj = ZipFile(zip_proj_bytes, "w")
    for file in dir_proj.rglob("*"):
        zip_proj.write(file, file.relative_to(dir_proj))
    zip_proj.close()
    zip_proj_bytes.seek(0)
    return zip_proj_bytes


def test_get_tools(client):
    response = client.get("/tools")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, dict)

    tools = get_tools()
    tools = {
        tool_name: tool.to_json()
        for tool_name, tool in tools.items()
        if tool is not None
    }
    assert data.keys() == tools.keys()
    for tool_name in tools.keys():
        assert data[tool_name] == tools[tool_name]


def test_tool_endpoints(client):
    tools = get_tools()
    for tool_name in tools.keys():
        response = client.get(f"/tools/{tool_name}")
        if tools[tool_name] is not None:
            assert response.status_code == 200
            data = json.loads(response.data)
            assert isinstance(data, dict)
        else:
            assert response.status_code == 500


def test_run_simulation_vitis(client: FlaskClient, test_proj_vitis: io.BytesIO):
    response = client.post(
        "/tools/vitis/run_simulation",
        content_type="application/octet-stream",
        data=test_proj_vitis,
    )

    assert response.status_code == 200

    proj_zip_out_bytes = io.BytesIO(response.data)
    proj_zip_out = ZipFile(proj_zip_out_bytes, "r")

    assert "vitis_hls.log" in proj_zip_out.namelist()
    assert proj_zip_out.open("vitis_hls.log").read() != b""

    proj_zip_out.close()


def test_run_synthesis_vitis(client: FlaskClient, test_proj_vitis: io.BytesIO):
    response = client.post(
        "/tools/vitis/run_synthesis",
        content_type="application/octet-stream",
        data=test_proj_vitis,
    )

    assert response.status_code == 200

    proj_zip_out_bytes = io.BytesIO(response.data)
    proj_zip_out = ZipFile(proj_zip_out_bytes, "r")

    assert "vitis_hls.log" in proj_zip_out.namelist()
    assert proj_zip_out.open("vitis_hls.log").read() != b""

    proj_zip_out.close()
