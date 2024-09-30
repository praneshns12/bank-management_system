from flask import Flask, session
from controllers import main_blueprint
from models import init_db

def create_app():
    app = Flask(__name__)
    app.secret_key = 'secret_key'
    app.register_blueprint(main_blueprint)
    
    with app.app_context():
        init_db()

    return app
