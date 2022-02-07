from flask import Blueprint
from flask_restx import Namespace, Api
from flask_servant.api import create_crud_operations
from typing import List, Any

_SERVICES = []

def create_service(name: str, description: str, path: str, model: Any, session=None, **kwargs) -> Namespace:
    ns = Namespace(name, description, path, **kwargs)

    create_crud_operations(model, ns, session=session)
    global _SERVICES
    _SERVICES.append(ns)
    return ns

def register_services(api: Api, namespaces: List[Namespace]):
    for ns in namespaces:
        api.add_namespace(ns)

def create_api(bp: Blueprint, title: str, description: str, namespaces: List[Namespace]=[], doc: str='/help', **kwargs) -> Api:
    swagger_api = Api(
        bp,
        title=title,
        description=description,
        doc='/'.join(filter(None, [bp.url_prefix or '', doc])),
        **kwargs
    )

    # if namespaces:
    register_services(swagger_api, namespaces or _SERVICES)
    
    return swagger_api