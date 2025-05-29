import os
from flask import Flask, jsonify, render_template, request, Blueprint

from ..logging import get_logger
from ..summary import get_summary
from ..settings import get_setting, write_setting
from ..db import init_db

from .notes import notes_bp
from .todos import todos_bp
from .actions import actions_bp
from .curiosities import curiosities_bp


logger = get_logger(__name__)


rest_server = Flask(__name__)

logger.debug


@rest_server.route("/")
def index():
    return render_template("index.html")


api_bp = Blueprint("api", __name__, url_prefix="/api")
api_bp.register_blueprint(notes_bp, url_prefix="/notes")
api_bp.register_blueprint(todos_bp, url_prefix="/todos")
api_bp.register_blueprint(actions_bp, url_prefix="/actions")
api_bp.register_blueprint(curiosities_bp, url_prefix="/curiosities")


@api_bp.get("/summary")
def handle_summary():
    prompt = request.args.get("prompt", "summarize all notes")
    try:
        title, summary = get_summary(prompt)
        # split the summary into chunks for easier rendering
        summary_chunks = summary.split("\n")
        return jsonify({"title": title, "summary": summary_chunks})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api_bp.get("/notebook")
def get_notebook():
    """
    Get the current notebook name.
    """
    notebook = get_setting("notebook")
    return jsonify({"notebook": notebook or "default"})


@api_bp.get("/notebooks")
def get_all_notebooks():
    """
    Get a list of all available notebooks.
    """
    notebooks_dir = os.path.join("data", "notebooks")
    notebooks = [
        f[:-3] for f in os.listdir(notebooks_dir) if f.endswith(".db")
    ]
    return jsonify({"notebooks": notebooks})


@api_bp.post("/notebook")
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


rest_server.register_blueprint(api_bp)


if __name__ == "__main__":
    rest_server.run(debug=True)
