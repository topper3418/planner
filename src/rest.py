from flask import Flask, jsonify, render_template, request

from .db import Note, Action, Todo, Annotation
from .summary import get_summary
from .setup_logging import setup_normal_logging
from .util import parse_time

import logging

setup_normal_logging()

logger = logging.getLogger(__name__)
rest_server = Flask(__name__)


@rest_server.route('/')
def index():
    return render_template('index.html')


@rest_server.post('/api/notes')
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


@rest_server.get('/api/notes')
def handle_notes():
    before_str = request.args.get('before')
    before = parse_time(before_str) if before_str else None
    after_str = request.args.get('after')
    after =  parse_time(after_str) if after_str else None
    search = request.args.get('search')
    limit = request.args.get('limit', default=25, type=int)

    try:
        notes = Note.get_all(before=before, after=after, search=search, limit=limit)
        notes.reverse()  # Match CLI behavior
        return jsonify({'notes': [note.model_dump() for note in notes]})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@rest_server.get('/api/todos')
def handle_todos():
    before = request.args.get('before')
    after = request.args.get('after')
    limit = request.args.get('limit', default=25, type=int)
    incomplete_only = request.args.get('incomplete_only', default=False, type=bool)
    complete_only = request.args.get('complete_only', default=False, type=bool)
    cancelled_only = request.args.get('cancelled_only', default=False, type=bool)

    if incomplete_only and complete_only:
        return jsonify({'error': 'Cannot use both incomplete_only and complete_only'}), 400

    complete = None
    if incomplete_only:
        complete = False
    elif complete_only:
        complete = True

    cancelled = cancelled_only

    try:
        todos = Todo.get_all(before=before, after=after, limit=limit, complete=complete, cancelled=cancelled)
        return jsonify({'todos': [todo.model_dump() for todo in todos]})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@rest_server.get('/api/actions')
def handle_actions():
    before = request.args.get('before')
    after = request.args.get('after')
    search = request.args.get('search')
    limit = request.args.get('limit', default=25, type=int)

    try:
        actions = Action.get_all(before=before, after=after, search=search, limit=limit)
        actions.reverse()
        return jsonify({'actions': [action.model_dump() for action in actions]})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@rest_server.get('/api/curiosities')
def handle_curiosities():
    before = request.args.get('before')
    after = request.args.get('after')
    search = request.args.get('search')
    limit = request.args.get('limit', default=25, type=int)

    try:
        annotations = Annotation.get_by_category_name('curiosity', before=before, after=after, search=search, limit=limit)
        if annotations is None:
            return jsonify({'curiosities': []})
        return jsonify({'curiosities': [annotation.model_dump() for annotation in annotations]})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@rest_server.get('/api/summary')
def handle_summary():
    prompt = request.args.get('prompt', 'summarize all notes')
    try:
        title, summary = get_summary(prompt)
        return jsonify({'title': title, 'summary': summary})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    rest_server.run(debug=True)
