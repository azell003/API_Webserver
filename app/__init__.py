from flask import Flask 
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app(config=None):
    app = Flask(__name__)
    if config:
        app.config.from_object(config)

    db.init_app(app)

    from app.routes.user import user
    app.register_blueprint(user)

    from app.routes.portfolio import portfolio
    app.register_blueprint(portfolio)

    with app.app_context():
        db.create_all()

    return app