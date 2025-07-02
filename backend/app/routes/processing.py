from flask import Blueprint, jsonify, current_app
from app import db
from app.models import Upload, ComparisonResult
from app.utils.ocr import process_upload
import os

bp = Blueprint('processing', __name__)

@bp.route('/<int:upload_id>', methods=['POST'])
def run_processing(upload_id):
    up = Upload.query.get_or_404(upload_id)
    if up.processed:
        return jsonify(message="Already processed", upload_id=upload_id), 200

    try:
        res = process_upload(upload_id)
    except ValueError as e:
        current_app.logger.warning(f"MRZ error for {upload_id}: {e}")
        return jsonify(error=str(e)), 400
    except Exception as e:
        current_app.logger.error(f"Unexpected error for {upload_id}", exc_info=e)
        return jsonify(error="Internal server error"), 500

    db.session.add(res)
    up.processed = True
    db.session.commit()

    return jsonify(result_id=res.id), 201
