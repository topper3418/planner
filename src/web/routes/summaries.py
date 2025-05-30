from flask import request, jsonify, Blueprint

from ...logging import get_logger
from ...summary import get_summary


summaries_bp = Blueprint("summaries", __name__)
logger = get_logger(__name__)


@summaries_bp.get("/query")
def handle_summary():
    prompt = request.args.get("prompt", "summarize all notes")
    try:
        title, summary = get_summary(prompt)
        # split the summary into chunks for easier rendering
        summary_chunks = summary.split("\n")
        return jsonify({"title": title, "summary": summary_chunks})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
