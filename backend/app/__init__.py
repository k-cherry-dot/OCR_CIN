from flask import Flask
from flask import send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_migrate import Migrate
import os

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__, instance_relative_config=False)
    CORS(app)
    app.config.from_object('app.config.Config')
    app.debug = True

    db.init_app(app)
    migrate.init_app(app, db)

    # register blueprints
    from .routes.uploads    import bp as uploads_bp
    from .routes.processing import bp as proc_bp
    from .routes.results    import bp as results_bp
    app.register_blueprint(uploads_bp, url_prefix='/api/uploads')
    app.register_blueprint(proc_bp,    url_prefix='/api/process')
    app.register_blueprint(results_bp, url_prefix='/api/results')

    # ────────────────────────────────────────────────────────────────────────
    # Serve Excel reports under /reports/<filename>
    reports_dir = os.path.join(os.getcwd(), 'uploads', 'reports')
    @app.route('/reports/<path:filename>')
    def reports(filename):
        # send the file as an attachment
        return send_from_directory(reports_dir, filename, as_attachment=True)
    # ────────────────────────────────────────────────────────────────────────

    return app



