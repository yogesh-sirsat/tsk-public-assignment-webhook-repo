from flask import Flask
from flask_cors import CORS

from app.webhook.routes import webhook
from app.extensions import mongo
import os


# Creating our flask app
def create_app():
    app = Flask(__name__)

    # enabling cors for requests from UI
    CORS(app)
    CORS(app, resources={r"/webhook/*": {"origins": os.getenv("FRONTEND_URL", "http://localhost:5173")}})

    # initializing mongodb
    mongo.init_app(app, uri=os.getenv("MONGODB_URI", "mongodb://localhost:27017/webhookEvents"))

    # registering all the blueprints
    app.register_blueprint(webhook)

    return app
