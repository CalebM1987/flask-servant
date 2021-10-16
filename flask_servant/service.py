from flask_restx import Namespace

def create_service(name: str, description: str, path: str, model, **kwargs) -> Namespace:
    ns = Namespace(name, description, path, **kwargs)