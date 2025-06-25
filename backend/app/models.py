from . import db
from datetime import datetime

class Upload(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    csv_filename = db.Column(db.String, nullable=False)
    pdf_filename = db.Column(db.String, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    processed = db.Column(db.Boolean, default=False)

class ComparisonResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    upload_id = db.Column(db.Integer, db.ForeignKey('upload.id'), nullable=False)
    data = db.Column(db.JSON, nullable=False)
    excel_path = db.Column(db.String, nullable=False)
