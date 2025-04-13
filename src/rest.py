import logging

from flask import Flask, jsonify, request

from . import db

logger = logging.getLogger(__name__)
rest_server = Flask(__name__)

@rest_server.post('/note')
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


    note= db.Note.create(note_text)
    return jsonify(note.model_dump()), 201
