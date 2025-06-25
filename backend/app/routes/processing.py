from flask import Blueprint, jsonify, current_app
from app import db
from app.models import Upload, ComparisonResult
from app.utils.ocr import process_upload

# Déclare ici ton Blueprint
bp = Blueprint('processing', __name__)

@bp.route('/<int:upload_id>', methods=['POST'])
def run_processing(upload_id):
    up = Upload.query.get_or_404(upload_id)
    if up.processed:
        return jsonify(message="Already processed", upload_id=upload_id), 200

    # Appelle ta fonction de traitement (à implémenter dans app/utils/ocr.py)
    res = process_upload(upload_id)
    db.session.add(res)
    up.processed = True
    db.session.commit()

    return jsonify(result_id=res.id), 201