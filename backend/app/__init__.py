from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object('app.config.Config')
    app.debug = True

    db.init_app(app)
    migrate.init_app(app, db)

    # register blueprints
    from .routes.uploads import bp as uploads_bp
    from .routes.processing import bp as proc_bp
    from .routes.results import bp as results_bp
    app.register_blueprint(uploads_bp, url_prefix='/api/uploads')
    app.register_blueprint(proc_bp,    url_prefix='/api/process')
    app.register_blueprint(results_bp, url_prefix='/api/results')

    return app


