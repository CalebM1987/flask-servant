from flask import Flask
from flask_socketio import SocketIO
import secrets

class SocketIORegistry(object):
    """singleton to store socketio instance"""
    _socketio = None
    _app = None
    _has_sockets = False
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(SocketIORegistry, cls).__new__(cls)
        return cls.instance

    @classmethod
    def register(cls, app: Flask):
        cls._app = app
        cls._socketio = SocketIO(app, cors_allowed_origins="*")
        cls._has_sockets = True
        return cls._app

    def run(cls, host: str=None, port: int=5000, **kwargs):
        if cls._has_sockets:
            return cls._socketio.run(cls._app, host, port, **kwargs)
        elif cls._app:
            return cls._app.run(host, port, **kwargs)

socketio = SocketIORegistry()

def create_app(name: str=None, app: Flask=None, secret_key: str=None, use_websockets: bool=True, **kwargs):
    if not app:
        app = Flask(name or __name__, **kwargs)
    print('create app kwargs: ', kwargs)
    if not app.config.get('SECRET_KEY'):
        app.config['SECRET_KEY'] = secret_key or secrets.token_urlsafe(32)
    return socketio.register(app)

def run_app(host: str=None, port: int=5000, **kwargs):
    return socketio.run(host, port, **kwargs)

def get_socket():
    if socketio._has_sockets:
        return socketio._socketio

