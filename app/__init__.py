from flask import Flask, request, send_from_directory, redirect
# from flask_socketio import SocketIO
import os

def create_app(debug=False):
    app = Flask(__name__)
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app
