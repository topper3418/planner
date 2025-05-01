import logging
from flask import request, jsonify, Blueprint

from ..db import Note, Annotation
from ..util import parse_time
from ..rendering import json_note


notes_bp = Blueprint('notes', __name__)
logger = logging.getLogger(__name__)


@notes_bp.post('/')
def create_note():
    """
    Create a new note.
    """
    payload = request.get_json()
    if not payload:
        return jsonify({'error': 'Invalid data'}), 400

    data = payload.get('data')
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    note_text = data.get('note')
    if not note_text:
        return jsonify({'error': 'No note provided'}), 400


    note= Note.create(note_text)
    return jsonify(note.model_dump()), 201


@notes_bp.get('/')
def handle_notes():
    # get args
    before_str = request.args.get('endTime')
    before = parse_time(before_str) if before_str else None
    after_str = request.args.get('startTime')
    after =  parse_time(after_str) if after_str else None
    search = request.args.get('search')
    limit = request.args.get('limit', default=25, type=int)
    try:
        notes = Note.get_all(before=before, after=after, search=search, limit=limit)
        notes.reverse()  # Match CLI behavior
        notes_json = [note.model_dump() for note in notes]
        return jsonify({'notes': notes_json})
    except Exception as e:
        logger.error(f"Error fetching notes: {e}")
        return jsonify({'error': str(e)}), 500


@notes_bp.get('/<int:note_id>')
def get_note_details(note_id):
    """
    Get details of a specific note.
    """
    try:
        note = Note.get_by_id(note_id)
        if note is None:
            return jsonify({'error': 'Note not found'}), 404
        details = json_note(note)
        return jsonify({'data': details})
    except Exception as e:
        logger.error(f"Error fetching note details: {e}")
        return jsonify({'error': str(e)}), 500
