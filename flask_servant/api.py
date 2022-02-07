from flask.json import jsonify
from flask_restx import Resource, Namespace
from flask_accepts import accepts, responds
from flask_servant.utils import get_route_name
from flask_servant.swagger import apply_fields
from flask_servant.orm import query_table
from flask_servant.schema import create_schema, FindResponseBase
from marshmallow import fields
from flask import request, jsonify
from typing import List
from flask_servant.websockets import get_socket


def create_crud_operations(table, ns: Namespace, exclude: List[str]=[], schema=None, session=None):
    if not schema:
        schema = create_schema(table, session=session)
    print('schema: ', schema)

    FindResponse = type(
        f'{table.__tablename__}FindResponse',
        (FindResponseBase,),
        dict(
            results=fields.List(
                fields.Nested(schema),
                many=True
            )   
        )
    )

    class Handler(Resource):
        parser = ns.parser()

        # set swagger docs
        apply_fields(parser, table, exclude)

        @ns.expect(parser, api=ns)
        @responds(schema=FindResponse, api=ns)
        def get(self):
            args = request.args
            results = schema(many=True).dump(query_table(table, session=session, **args))
            socket = get_socket()
            print('socket yo??', socket)
            if socket:
                socket.emit('find', results)
                print('emitted')
            return jsonify(
                dict(
                    results=results,
                    total=len(results),
                    count=len(results),
                    page=None,
                    paginated=False,
                    totalPages=None
                )
            )


        @accepts(schema=schema, api=ns)
        def post(self):
            payload = request.json
            record = schema().load(payload)
            print('record is: ', record)
            session.add(record)
            session.commit()
            socket = get_socket()
            if socket:
                socket.emit(f'{get_route_name(table)}/create', schema().dump(record))
            return jsonify({ 'status': 'success' })

    class NestedHandler(Resource):
        
        @responds(schema=schema, api=ns)
        def get(self, id):
            obj = session.query(table).get(id)
            return obj

        def _updater(self, id):
            jsonObj = request.json
            obj = session.query(table).get(id)
            for prop, val in jsonObj.items():
                if hasattr(obj, prop):
                    setattr(obj, prop, val)
            session.commit()
            return obj

        @responds(schema=schema, api=ns)
        def put(self, id):
            return self._updater(id)

        @responds(schema=schema, api=ns)
        def patch(self, id):
            return self._updater(id)

        @responds(schema=schema, api=ns)
        def delete(self, id):
            obj = session.query(table).get(id)
            obj.delete() if hasattr(obj, 'delete') else session.delete(obj)
            session.commit()
            return obj

    
    getterType = type(f'{table.__tablename__}Handler', (Handler,), {})
    nestedGetterType = type(f'{table.__tablename__}NestedHandler', (NestedHandler, ), {})
    print('getterType: ', getterType, getterType.get)
        
    ns.route(f'/{get_route_name(table)}')(getterType)
    ns.route(f'/{get_route_name(table)}/<id>')(nestedGetterType)

    return ns



