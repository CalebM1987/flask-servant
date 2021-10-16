from flask_restx import Resource, Namespace
from flask_accepts import accepts, responds
from flask_servant.utils import get_route_name
from flask_servant.swagger import apply_fields
from flask_servant.orm import query_table
from typing import List

def get_resource_wrapper(table, ns: Namespace, prefix='CRUD'):
    name = 'Test'
    return ns.route('/{}'.format(get_route_name(table)))(type('{}{}'.format(prefix, name), (Resource,), {}))

def create_crud(table, ns: Namespace, exclude: List[str]=[]):
    klass = get_resource_wrapper(table, ns)
    parser = ns.parser()

    # set swagger docs
    apply_fields(parser, table, exclude)

    @ns.expect(parser, api=ns)
    @responds(schema=schema, api=ns)
    def get(self):
        return query_table()

    klass.get = get

    return ns



