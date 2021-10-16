import six
import datetime
from utils import get_columns

# RESTX-FIELDS-CONVERSION
RESTX_FIELDS_MAPPER = {
    'String': str,
    'FormattedString': str,
    'Integer': int,
    'Nested': dict,
    'List': list,
    'Boolean': bool,
    'Float': float,
    'Date': datetime.date,
    'DateTime': datetime.datetime,
    'Time': datetime.time
}

PARSER_FIELDS_MAPPER = RESTX_FIELDS_MAPPER.copy()
for key in ['Date', 'DateTime', 'Time']:
    PARSER_FIELDS_MAPPER[key] = str
for key in ['Nested', 'List']:
    PARSER_FIELDS_MAPPER[key] = None


QUERY_HELPERS = [
    {
        "name": "$fields",
        "kwargs": {
            "type": str
        }
    },
    {
        "name": "$limit",
        "kwargs": {
            "type": int,
            "help": "Maximum number of results"
        }
    }
]

def apply_fields(parser, model_or_schema=None, exclude=[]):
    """
    """
    _defaults = dict(
        default=None,
        required=False,
        location='args'
    )

    qs = []
    getName = lambda c: c.__name__ if hasattr(c, '__name__') else c.__class__.__name__.split('.')[-1]

    if not model_or_schema:
        return parser

    # declarative base
    if hasattr(model_or_schema, '__table__'):
        cols = get_columns(model_or_schema)
        for col in cols:
            if col.name not in exclude:
                try:
                    dtype = col.type.python_type
                    if dtype:
                        qs.append(
                            dict(
                                name=col.name,
                                type=dtype,
                                help=col.doc
                            )
                        )
                except:
                    continue

    # api.Model check
    elif hasattr(model_or_schema, 'items'):
        for name, _model in model_or_schema.items():
            if name not in exclude:
                model_type = getName(_model)
                if model_type:
                    qs.append(
                        dict(
                            name=name,
                            type=model_type,
                        )
                    )

    else:
        # it is a marshmallow.Schema
        dec_fields = model_or_schema._declared_fields if hasattr(model_or_schema, '_declared_fields') \
            else (model_or_schema.declared_fields if hasattr(model_or_schema, 'declared_fields') else [])

        for name, _schema in six.iteritems(dec_fields):
            model_type = PARSER_FIELDS_MAPPER.get(getName(_schema), str)
            if model_type and name not in exclude:
                qs.append(
                    dict(
                        name=name,
                        type=model_type,
                        help=_schema.metadata.get('description') if hasattr(_schema, 'metadata') else None
                    )
                )

    example_fields = ','.join(list(map(lambda f: f.get('name'), qs[:3]))) if qs else 'fieldA,fieldB'

    qs.extend(QUERY_HELPERS)

    for arg in qs:
        arg.update(_defaults)
        if arg.get('name') == '$fields':
            arg['help'] = 'comma separated list of fields to return (example: "{}")'.format(example_fields)
        parser.add_argument(**arg)

    return parser