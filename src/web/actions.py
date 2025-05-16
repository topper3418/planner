import logging
from flask import request, jsonify, Blueprint

from ..logging import get_logger
from ..db import Action
from ..rendering import json_action


actions_bp = Blueprint("actions", __name__)
logger = get_logger(__name__)


@actions_bp.get("/")
def handle_actions():
    before = request.args.get("endTime")
    after = request.args.get("startTime")
    search = request.args.get("search")
    limit = request.args.get("limit", default=25, type=int)
    applied_to_todo = request.args.get("appliedToTodo")
    if applied_to_todo is not None:
        applied_to_todo = applied_to_todo.lower() == "true"
    try:
        actions = Action.get_all(
            before=before,
            after=after,
            search=search,
            limit=limit,
            applied_to_todo=applied_to_todo,
        )
        actions.reverse()
        actions_json = [action.model_dump() for action in actions]
        # add the affected todos, where applicable
        for action, action_dict in zip(actions, actions_json):
            if action.todo:
                action_dict["todo"] = action.todo.model_dump()
        return jsonify({"actions": actions_json})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@actions_bp.get("/<int:action_id>")
def get_action_details(action_id):
    try:
        action = Action.get_by_id(action_id)
        if action is None:
            return jsonify({"error": "Action not found"}), 404
        details = json_action(action)
        return jsonify({"data": details})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
