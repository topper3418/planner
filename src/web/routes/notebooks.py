import os
from flask import request, jsonify, Blueprint

from ...db import init_db

from ...settings import get_setting, write_setting

from ...logging import get_logger


notebooks_bp = Blueprint("notebooks", __name__)
logger = get_logger(__name__)


@notebooks_bp.get("/")
def handle_todos():
    """
    Get a list of all available notebooks.
    """
    notebooks_dir = os.path.join("data", "notebooks")
    notebooks = [
        f[:-3] for f in os.listdir(notebooks_dir) if f.endswith(".db")
    ]
    return jsonify({"notebooks": notebooks})


@notebooks_bp.post("/")
def create_notebook():
    """
    Create a new notebook.
    """
    request_data = request.json
    if not request_data:
        return jsonify({"error": "Request body is required"}), 400
    new_notebook = request_data.get("notebook")
    if not new_notebook:
        return jsonify({"error": "Notebook name is required"}), 400
    notebook_path = os.path.join("data", "notebooks", f"{new_notebook}.db")
    if os.path.exists(notebook_path):
        return jsonify({"error": "Notebook already exists"}), 400
    write_setting("notebook", new_notebook)
    init_db()
    return jsonify({"notebook": new_notebook}), 201


@notebooks_bp.get("/active")
def get_notebook():
    """
    Get the current notebook name.
    """
    notebook = get_setting("notebook")
    return jsonify({"notebook": notebook or "default"})


@notebooks_bp.post("/active")
def set_notebook():
    """
    Set the current notebook name.
    """
    request_data = request.json
    if not request_data:
        return jsonify({"error": "Request body is required"}), 400
    new_notebook = request_data.get("notebook")
    if not new_notebook:
        return jsonify({"error": "Notebook name is required"}), 400
    write_setting("notebook", new_notebook)
    # see if the notebook is new
    if not os.path.exists(
        os.path.join("data", "notebooks", f"{new_notebook}.db")
    ):
        init_db()
    return jsonify({"notebook": new_notebook})
