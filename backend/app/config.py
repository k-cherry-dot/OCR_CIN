import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', '134340')
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'postgresql://postgres:134340@localhost:5432/ocr_cin_db'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER_CSV = os.path.join(os.getcwd(), 'uploads', 'csv')
    UPLOAD_FOLDER_PDF = os.path.join(os.getcwd(), 'uploads', 'pdf')
