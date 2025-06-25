from flask import Blueprint, request, jsonify, current_app
from app.utils.storage import save_file
from app.models import Upload
from app import db

# ← Vérifie que tu appelles bien ta variable 'bp'
bp = Blueprint('uploads', __name__)

@bp.route('/csv', methods=['POST'])
def upload_csv():
    f = request.files.get('file')
    if not f:
        return jsonify(error="No file"), 400
    fname, path = save_file(f, current_app.config['UPLOAD_FOLDER_CSV'])
    up = Upload(csv_filename=fname, pdf_filename='')
    db.session.add(up); db.session.commit()
    return jsonify(upload_id=up.id), 201

@bp.route('/pdf', methods=['POST'])
def upload_pdf():
    upload_id = request.form.get('upload_id')
    f = request.files.get('file')
    if not f or not upload_id:
        return jsonify(error="Missing"), 400
    up = Upload.query.get(upload_id)
    if not up:
        return jsonify(error="Invalid upload_id"), 404
    fname, path = save_file(f, current_app.config['UPLOAD_FOLDER_PDF'])
    up.pdf_filename = fname
    db.session.commit()
    return jsonify(upload_id=up.id), 200