from flask import Flask, jsonify, render_template, request, Blueprint

from ..logging import get_logger
from ..summary import get_summary

from .notes import notes_bp
from .todos import todos_bp
from .actions import actions_bp
from .curiosities import curiosities_bp


logger = get_logger(__name__)
rest_server = Flask(__name__)

logger.debug


@rest_server.route('/')
def index():
    return render_template('index.html')


api_bp = Blueprint('api', __name__, url_prefix='/api')
api_bp.register_blueprint(notes_bp, url_prefix='/notes')
api_bp.register_blueprint(todos_bp, url_prefix='/todos')
api_bp.register_blueprint(actions_bp, url_prefix='/actions')
api_bp.register_blueprint(curiosities_bp, url_prefix='/curiosities')


@api_bp.get('/summary')
def handle_summary():
    prompt = request.args.get('prompt', 'summarize all notes')
    try:
        title, summary = get_summary(prompt)
        # split the summary into chunks for easier rendering
        summary_chunks = summary.split('\n')
        return jsonify({'title': title, 'summary': summary_chunks})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

rest_server.register_blueprint(api_bp)


if __name__ == '__main__':
    rest_server.run(debug=True)
