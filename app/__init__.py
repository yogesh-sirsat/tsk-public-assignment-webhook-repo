from flask import Flask
from flask_cors import CORS

from app.webhook.routes import webhook
from app.extensions import mongo


# Creating our flask app
def create_app():
    app = Flask(__name__)

    # enabling cors for requests from UI
    CORS(app)
    CORS(app, resources={r"/webhook/*": {"origins": "http://localhost:5173"}})

    # initializing mongodb
    mongo.init_app(app, uri="mongodb://localhost:27017/webhookEvents")

    # registering all the blueprints
    app.register_blueprint(webhook)

    return app
