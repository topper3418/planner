from flask import request, jsonify, Blueprint

from ...logging import get_logger
from ...db import Curiosity
from ...rendering import json_curiosity


curiosities_bp = Blueprint("curiosities", __name__)
logger = get_logger(__name__)


@curiosities_bp.get("/")
def handle_curiosities():
    before = request.args.get("endTime")
    after = request.args.get("startTime")
    search = request.args.get("search")
    limit = request.args.get("limit", default=25, type=int)
    try:
        curiosities = Curiosity.get_all(
            before=before, after=after, search=search, limit=limit
        )
        curiosity_jsons = [
            curiosity.model_dump() for curiosity in curiosities
        ]
        for curiosity_json, curiosity in zip(curiosity_jsons, curiosities):
            curiosity_json["note"] = curiosity.source_note.model_dump()
        logger.info(f"Fetched {len(curiosity_jsons)} curiosities")
        curiosity_jsons.reverse()  # Match CLI behavior
        return jsonify({"curiosities": curiosity_jsons})
    except Exception as e:
        logger.error(f"Error fetching curiosities: {e}")
        return jsonify({"error": str(e)}), 500


@curiosities_bp.get("/<int:curiosity_id>")
def get_curiosity_details(curiosity_id):
    try:
        curiosity = Curiosity.get_by_id(curiosity_id)
        if curiosity is None:
            return jsonify({"error": "Curiosity not found"}), 404
        details = json_curiosity(curiosity)
        return jsonify({"data": details})
    except Exception as e:
        logger.error(f"Error fetching curiosity details: {e}")
        return jsonify({"error": str(e)}), 500
