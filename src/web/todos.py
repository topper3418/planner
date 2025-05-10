from flask import request, jsonify, Blueprint

from ..logging import get_logger
from ..db import Todo
from ..rendering import json_todo


todos_bp = Blueprint("todos", __name__)
logger = get_logger(__name__)


@todos_bp.get("/")
def handle_todos():
    before = request.args.get("endTime", type=str)
    after = request.args.get("startTime", type=str)
    limit = request.args.get("limit", default=25, type=int)
    search = request.args.get("search", type=str)
    show_complete = request.args.get("completed") == "true"
    show_cancelled = request.args.get("cancelled") == "true"
    show_active = request.args.get("active") == "true"

    try:
        todos = Todo.get_all(
            before=before,
            after=after,
            limit=limit,
            complete=show_complete,
            cancelled=show_cancelled,
            active=show_active,
            search=search,
        )
        return jsonify({"todos": [todo.model_dump() for todo in todos]})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@todos_bp.get("/<int:todo_id>")
def get_todo_details(todo_id):
    try:
        todo = Todo.get_by_id(todo_id)
        if todo is None:
            return jsonify({"error": "Todo not found"}), 404
        details = json_todo(todo)
        return jsonify({"data": details})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
