from rev_manager.factory import create_flask_app


flask_app, celery_app = create_flask_app()
print('Flask_APP-OK')