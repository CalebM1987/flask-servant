from flask.json import jsonify
from flask_restx import Resource, Namespace
from flask_accepts import accepts, responds
from flask_servant.utils import get_route_name
from flask_servant.swagger import apply_fields
from flask_servant.orm import query_table
from flask_servant.schema import create_schema
from flask import request, jsonify
from typing import List


def create_crud_operations(table, ns: Namespace, exclude: List[str]=[], schema=None, session=None):
   
    if not schema:
        schema = create_schema(table, session=session)
    print('schema: ', schema)

    class Handler(Resource):
        parser = ns.parser()

        # set swagger docs
        apply_fields(parser, table, exclude)

        @ns.expect(parser, api=ns)
        @responds(schema=schema(many=True), api=ns)
        def get(self):
            return query_table(table, session=session)

        @accepts(schema=schema, api=ns)
        def post(self):
            payload = request.json
            record = schema().load(payload)
            print('record is: ', record)
            session.add(record)
            session.commit()
            return jsonify({ 'status': 'success' })

    
    getterType = type('PointGetter', (Handler,), {})
    print('getterType: ', getterType, getterType.get)
        
    ns.route('/{}'.format(get_route_name(table)))(getterType)

    return ns



