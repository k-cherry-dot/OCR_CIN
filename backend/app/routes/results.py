from flask import Blueprint, jsonify, send_file
from app.models import ComparisonResult

bp = Blueprint('results', __name__)

@bp.route('/<int:upload_id>', methods=['GET'])
def get_results(upload_id):
    res = ComparisonResult.query.filter_by(upload_id=upload_id).first_or_404()
    return jsonify(data=res.data, excel_url=f"/api/results/{res.id}/download")

@bp.route('/<int:result_id>/download', methods=['GET'])
def download_excel(result_id):
    res = ComparisonResult.query.get_or_404(result_id)
    return send_file(res.excel_path, as_attachment=True)
