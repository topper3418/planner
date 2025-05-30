from flask import Blueprint
from .routes import (
    notes_bp,
    todos_bp,
    actions_bp,
    curiosities_bp,
    notebooks_bp,
    summaries_bp,
)


api_bp = Blueprint("api", __name__, url_prefix="/api")
api_bp.register_blueprint(notes_bp, url_prefix="/notes")
api_bp.register_blueprint(todos_bp, url_prefix="/todos")
api_bp.register_blueprint(actions_bp, url_prefix="/actions")
api_bp.register_blueprint(curiosities_bp, url_prefix="/curiosities")
api_bp.register_blueprint(notebooks_bp, url_prefix="/notebooks")
api_bp.register_blueprint(summaries_bp, url_prefix="/summaries")
