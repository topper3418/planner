import logging
from flask import request, jsonify, Blueprint

from ..db import Annotation
from ..rendering import json_curiosity


curiosities_bp = Blueprint('curiosities', __name__)
logger = logging.getLogger(__name__)


@curiosities_bp.get('/')
def handle_curiosities():
    logger.warning('Fetching curiosities')
    before = request.args.get('endTime')
    after = request.args.get('startTime')
    search = request.args.get('search')
    limit = request.args.get('limit', default=25, type=int)
    try:
        logger.warning(f"Fetching curiosities with before={before}, after={after}, search={search}, limit={limit}")
        annotations = Annotation.get_by_category_name('curiosity', before=before, after=after, search=search, limit=limit)
        logger.warning(f"Curiosities found: {annotations}")
        curiosities = [annotation.model_dump() for annotation in annotations]
        for curiosity, annotation in zip(curiosities, annotations):
            curiosity['note'] = annotation.note.model_dump()
        return jsonify({'curiosities': curiosities})
    except Exception as e:
        logger.error(f"Error fetching curiosities: {e}")
        return jsonify({'error': str(e)}), 500


@curiosities_bp.get('/<int:annotation_id>')
def get_curiosity_details(annotation_id):
    try:
        annotation = Annotation.get_by_id(annotation_id)
        if annotation is None:
            return jsonify({'error': 'Curiosity not found'}), 404
        details = json_curiosity(annotation)
        return jsonify({'data': details})
    except Exception as e:
        logger.error(f"Error fetching curiosity details: {e}")
        return jsonify({'error': str(e)}), 500
