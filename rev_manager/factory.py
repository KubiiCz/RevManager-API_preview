from flask import Flask
from flask_cors import CORS

def create_flask_app():
    flask_app = Flask(__name__)
    flask_app.config.from_object("rev_manager.config.Config")
    with flask_app.app_context():
        CORS(flask_app)

        # DATABASE
        from rev_manager.database import init_db
        init_db()

        from .endpoints import api_hp_bp
        flask_app.register_blueprint(api_hp_bp, url_prefix='{prefix}/'.format(prefix='/api'))

        ## INIT CELERY
        from rev_manager import celery
        from rev_manager.celery_utils import make_celery
        celery_app = make_celery(celery, flask_app)

        return flask_app, celery_app