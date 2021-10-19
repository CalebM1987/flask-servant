from flask import Blueprint
from flask_restx import Namespace, Api
from flask_servant.api import create_crud_operations
from typing import List

def create_service(name: str, description: str, path: str, model, session=None, **kwargs) -> Namespace:
    ns = Namespace(name, description, path, **kwargs)

    create_crud_operations(model, ns, session=session)

    return ns

def register_services(api: Api, namespaces: List[Namespace]):
    for ns in namespaces:
        api.add_namespace(ns)

def create_api(bp: Blueprint, title: str, description: str, namespaces: List[Namespace]=[], doc: str='/help', **kwargs) -> Api:
    swagger_api = Api(
        bp,
        title=title,
        description=description,
        doc=doc,
        **kwargs
    )

    if namespaces:
        register_services(swagger_api, namespaces)
    
    return swagger_api