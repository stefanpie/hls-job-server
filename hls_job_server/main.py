import argparse
import io
import shutil
import subprocess
from abc import ABC, abstractmethod
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Union
from zipfile import ZipFile

from flask import Flask, render_template, request, send_file

DIR_CURRENT = Path(__file__).parent


def find_bin_which(bin_name: str) -> Path | None:
    match = shutil.which(bin_name)
    if match is not None:
        return Path(match)
    return None


class Tool(ABC):
    def __init__(self, tool_bins: dict[str, Path] = {}, env_vars: dict[str, str] = {}):
        self.tool_bins = tool_bins
        self.env_vars = env_vars

    @abstractmethod
    def run_simulation(
        self,
        proj_zip: io.BytesIO,
    ) -> io.BytesIO: ...

    @abstractmethod
    def run_synthesis(
        self,
        proj_zip: io.BytesIO,
    ) -> io.BytesIO: ...

    @classmethod
    @abstractmethod
    def auto_find(cls) -> Union["Tool", None]: ...

    def to_json(self):
        return {
            "tool_bins": {k: str(v) for k, v in self.tool_bins.items()},
            "env_vars": {k: str(v) for k, v in self.env_vars.items()},
        }


class Vitis(Tool):
    def __init__(self, tool_bins: dict[str, Path] = {}, env_vars: dict[str, str] = {}):
        super().__init__(tool_bins=tool_bins, env_vars=env_vars)

    def run_simulation(
        self,
        proj_zip_stream: io.BytesIO,
    ) -> io.BytesIO:
        try:
            proj_zip = ZipFile(proj_zip_stream, "r")
        except Exception as e:
            raise e

        # make a temp dir
        tempdir_project = TemporaryDirectory()
        tempdir_project_path = Path(tempdir_project.name)

        # extract the zip
        proj_zip.extractall(tempdir_project_path)
        proj_zip.close()

        # handle case where the zip has a top level directory, the user probably zipped the project folder
        top_level_files = list(tempdir_project_path.iterdir())
        if len(top_level_files) == 1 and top_level_files[0].is_dir():
            for file in top_level_files[0].iterdir():
                file.rename(tempdir_project_path / file.name)
            top_level_files[0].rmdir()

        fp_hls_simulation_tcl = tempdir_project_path / "hls_simulation.tcl"

        if not fp_hls_simulation_tcl.exists():
            raise FileNotFoundError("hls_simulation.tcl not found")

        bin_vitis_hls = self.tool_bins["vitis_hls"]
        subprocess.run(
            [bin_vitis_hls, str(fp_hls_simulation_tcl)],
            cwd=tempdir_project_path,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            bufsize=0,
            timeout=10 * 60,
        )

        proj_zip_out_bytes = io.BytesIO()
        proj_zip_out = ZipFile(proj_zip_out_bytes, "w")
        for file in tempdir_project_path.rglob("*"):
            proj_zip_out.write(file, file.relative_to(tempdir_project_path))
        proj_zip_out.close()
        proj_zip_out_bytes.seek(0)

        tempdir_project.cleanup()

        return proj_zip_out_bytes

    def run_synthesis(self, proj_zip_stream: io.BytesIO) -> io.BytesIO:
        try:
            proj_zip = ZipFile(proj_zip_stream, "r")
        except Exception as e:
            raise e

        # make a temp dir
        tempdir_project = TemporaryDirectory()
        tempdir_project_path = Path(tempdir_project.name)

        # extract the zip
        proj_zip.extractall(tempdir_project_path)
        proj_zip.close()

        # handle case where the zip has a top level directory, the user probably zipped the project folder
        top_level_files = list(tempdir_project_path.iterdir())
        if len(top_level_files) == 1 and top_level_files[0].is_dir():
            for file in top_level_files[0].iterdir():
                file.rename(tempdir_project_path / file.name)
            top_level_files[0].rmdir()

        fp_hls_synthesis_tcl = tempdir_project_path / "hls_synthesis.tcl"

        if not fp_hls_synthesis_tcl.exists():
            raise FileNotFoundError("hls_synthesis.tcl not found")

        bin_vitis_hls = self.tool_bins["vitis_hls"]
        subprocess.run(
            [bin_vitis_hls, str(fp_hls_synthesis_tcl)],
            cwd=tempdir_project_path,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            bufsize=0,
            timeout=10 * 60,
        )

        proj_zip_out_bytes = io.BytesIO()
        proj_zip_out = ZipFile(proj_zip_out_bytes, "w")
        for file in tempdir_project_path.rglob("*"):
            proj_zip_out.write(file, file.relative_to(tempdir_project_path))
        proj_zip_out.close()
        proj_zip_out_bytes.seek(0)

        tempdir_project.cleanup()

        return proj_zip_out_bytes

    @classmethod
    def auto_find(cls: type["Vitis"]) -> Union["Vitis", None]:
        tool_bins_matches = {
            "vitis": find_bin_which("vitis"),
            "vitis-run": find_bin_which("vitis-run"),
            "vitis_hls": find_bin_which("vitis_hls"),
            "vivado": find_bin_which("vivado"),
        }
        if not all(tool_bins_matches.values()):
            return None
        tool_bins: dict[str, Path] = {
            k: v for k, v in tool_bins_matches.items() if v is not None
        }

        return cls(
            tool_bins=tool_bins,
        )


class Catapult(Tool):
    def run_simulation(self, *args, **kwargs):
        raise NotImplementedError

    def run_synthesis(self, *args, **kwargs):
        raise NotImplementedError

    @classmethod
    def auto_find(cls) -> Union["Catapult", None]:
        tool_bins_matches = {
            "catapult": find_bin_which("catapult"),
        }
        if not all(tool_bins_matches.values()):
            return None
        tool_bins: dict[str, Path] = {
            k: v for k, v in tool_bins_matches.items() if v is not None
        }
        return cls(
            tool_bins=tool_bins,
        )


class IntelHLS(Tool):
    def run_simulation(self, *args, **kwargs):
        raise NotImplementedError

    def run_synthesis(self, *args, **kwargs):
        raise NotImplementedError

    @classmethod
    def auto_find(cls) -> Union["IntelHLS", None]:
        return None


class XLS(Tool):
    def run_simulation(self, *args, **kwargs):
        raise NotImplementedError

    def run_synthesis(self, *args, **kwargs):
        raise NotImplementedError

    @classmethod
    def auto_find(cls) -> Union["XLS", None]:
        return None


def get_tools():
    tools = {
        "vitis": Vitis.auto_find(),
        "catapult": Catapult.auto_find(),
        "intel_hls": IntelHLS.auto_find(),
        "xls": XLS.auto_find(),
    }
    return tools


def build_app() -> Flask:
    tools = get_tools()
    app = Flask("hls_job_server", template_folder=DIR_CURRENT / "html_templates")
    app.config["TEMPLATES_AUTO_RELOAD"] = True

    @app.route("/")
    def index():
        return render_template("index.html.jinja", tools=tools)

    # add get_tools endpoint
    @app.route("/tools")
    def get_tools_endpoint():
        return {
            tool_name: tool.to_json()
            for tool_name, tool in tools.items()
            if tool is not None
        }

    # create a route for each tool
    for tool_name, tool in tools.items():

        def make_tool_endpoint(tool):
            def tool_endpoint():
                return tool.to_json()

            return tool_endpoint

        app.add_url_rule(
            f"/tools/{tool_name}",
            endpoint=f"{tool_name}_endpoint",
            view_func=make_tool_endpoint(tool),
        )

        def make_run_simulation_endpoint(tool: Tool):
            def run_simulation_endpoint():
                try:
                    binary_data = request.get_data()
                    binary_stream = io.BytesIO(binary_data)
                    proj_zip_out_bytes = tool.run_simulation(binary_stream)
                    return send_file(
                        proj_zip_out_bytes,
                        mimetype="application/octet-stream",
                    )
                except Exception as e:
                    app.logger.error(e)
                    return str(e), 500

            return run_simulation_endpoint

        # Add the endpoint to the app
        app.add_url_rule(
            f"/tools/{tool_name}/run_simulation",
            endpoint=f"{tool_name}_run_simulation",
            view_func=make_run_simulation_endpoint(tool),
            methods=["POST"],
        )

        def make_run_synthesis_endpoint(tool: Tool):
            def run_synthesis_endpoint():
                try:
                    binary_data = request.get_data()
                    binary_stream = io.BytesIO(binary_data)
                    proj_zip_out_bytes = tool.run_synthesis(binary_stream)
                    return send_file(
                        proj_zip_out_bytes,
                        mimetype="application/octet-stream",
                    )
                except Exception as e:
                    app.logger.error(e)
                    return str(e), 500

            return run_synthesis_endpoint

        app.add_url_rule(
            f"/tools/{tool_name}/run_synthesis",
            endpoint=f"{tool_name}_run_synthesis",
            view_func=make_run_synthesis_endpoint(tool),
            methods=["POST"],
        )

    @app.after_request
    def add_header(r):
        """
        Add headers to both force latest IE rendering engine or Chrome Frame,
        and also to cache the rendered page for 10 minutes.
        """
        r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        r.headers["Pragma"] = "no-cache"
        r.headers["Expires"] = "0"
        r.headers["Cache-Control"] = "public, max-age=0"
        return r

    return app


def main(args: argparse.Namespace):
    app = build_app()
    app.run(host="localhost", port=args.port, debug=args.debug)


def cli():
    parser = argparse.ArgumentParser(description="HLS Job Server")
    parser.add_argument("--port", type=int, default=5000, help="Port to listen on")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")

    args = parser.parse_args()
    main(args)


if __name__ == "__main__":
    cli()
