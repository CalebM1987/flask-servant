import stat
from flask.json import jsonify
from flask_restx import Resource, Namespace
from flask_accepts import accepts, responds
from flask_servant.pagination import PAGINATION_CACHE, Paginator
from flask_servant.utils import get_route_name, get_typed_query_param
from flask_servant.swagger import apply_fields
from flask_servant.orm import query_table
from flask_servant.schema import create_schema, FindResponseBase
from marshmallow import fields
from flask import request, jsonify
from typing import List
from flask_servant.websockets import get_socket

SESSION_COOKIE = 'X-FLASK-SERVANT-QUERY-SESSION'

def create_crud_operations(table, ns: Namespace, exclude: List[str]=[], schema=None, session=None):
    if not schema:
        schema = create_schema(table, session=session)

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
            query_kwargs, special_kwargs = {}, {}
            for k,v in request.args.items():
                if k.startswith('$'):
                    special_kwargs[k] = v
                else:
                    query_kwargs[k] = v
            
            # first check for cached query
            paginator, query = None, None
            cached_query_cookie_name = f'{SESSION_COOKIE}__{get_route_name(table)}'
            session_cookie = request.cookies.get(cached_query_cookie_name)
            page = get_typed_query_param(special_kwargs, '$page', int)
            session_uid = special_kwargs.get('$session_uid') or session_cookie
            if session_uid and page:
                # pull from paginated results cache
                print('session cookie: ', session_uid, session_cookie)
                paginator = PAGINATION_CACHE.get(session_uid)
                print('pulled cached pagination result?', paginator)
                if paginator:
                    query = paginator.query

            if not query:
                # no cached query, fetch new query
                print('found no cached queries, forming new one')
                query = query_table(table, session=session, **query_kwargs)

            schemaKwargs = { 'many': True }
            fields = get_typed_query_param(special_kwargs, '$fields', list)
            offset = get_typed_query_param(special_kwargs, '$offset', int)
            limit = get_typed_query_param(special_kwargs, '$limit', int)
            
            if fields:
                schemaKwargs['only'] = fields

            results = []
            
            if page or limit:
                if not paginator:
                    paginator = Paginator(query, int(limit or offset or '50'))
                    PAGINATION_CACHE.add(paginator)

                # return paginated results with user defined page or default to 1
                results = paginator.getPage(page or 1)

            elif offset:
                results = query.offset(int(offset))
            else:
                results = query.all()

            serialized_results = schema(**schemaKwargs).dump(results)
            socket = get_socket()

            if socket:
                socket.emit(f'{get_route_name(table)}/find', {"results": serialized_results, 'params': request.args.to_dict() })
            result_count = len(serialized_results)

            # return find response
            response = jsonify(
                dict(
                    count=result_count,
                    paginated=paginator is not None,
                    results=serialized_results,
                    total=paginator.total if paginator else result_count,
                    page=paginator.currentPage if paginator else None,
                    totalPages=paginator.pages if paginator else None,
                    session_uid=paginator.id if paginator else None
                )
            )

            if paginator and paginator.id != session_cookie:
                print('setting new session cookie: ', paginator.id)
                response.set_cookie(
                    cached_query_cookie_name, 
                    paginator.id, 
                    expires=paginator.expires
                )

            return response


        @accepts(schema=schema, api=ns)
        @responds(schema=schema, status_code=201, api=ns)
        def post(self):
            payload = request.json
            record = schema().load(payload)
            session.add(record)
            session.commit()
            socket = get_socket()
            entity = schema().dump(record)
            if socket:
                socket.emit(f'{get_route_name(table)}/create', entity)
            return record
            # return jsonify({ 'status': 'success', 'entity': entity })

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

        @accepts(schema=schema, api=ns)
        @responds(schema=schema, api=ns)
        def put(self, id):
            obj = self._updater(id)
            entity = schema().dump(obj)
            socket = get_socket()
            if socket:
                socket.emit(f'{get_route_name(table)}/put', entity)
            return entity

        @accepts(schema=schema, api=ns)
        @responds(schema=schema, api=ns)
        def patch(self, id):
            obj = self._updater(id)
            entity = schema().dump(obj)
            socket = get_socket()
            if socket:
                socket.emit(f'{get_route_name(table)}/patch', entity)
            return entity

        @responds(schema=schema, api=ns)
        def delete(self, id):
            obj = session.query(table).get(id)
            obj.delete() if hasattr(obj, 'delete') else session.delete(obj)
            session.commit()
            entity = schema().dump(obj)
            socket = get_socket()
            if socket:
                socket.emit(f'{get_route_name(table)}/delete', entity)
            return obj

    
    getterType = type(f'{table.__tablename__}Handler', (Handler,), {})
    nestedGetterType = type(f'{table.__tablename__}NestedHandler', (NestedHandler, ), {})
    print('getterType: ', getterType, getterType.get)
        
    ns.route(f'/{get_route_name(table)}')(getterType)
    ns.route(f'/{get_route_name(table)}/<id>')(nestedGetterType)

    return ns



