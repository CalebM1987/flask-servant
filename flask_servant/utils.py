import re
import sqlalchemy
from werkzeug.datastructures import MultiDict
from typing import Union, Dict, Any

def get_primary_key(table):
    return sqlalchemy.inspection.inspect(table).primary_key[0]
    

def get_columns(table):
    """gets the raw column objects
    Args:
        table: the table
    Returns:
        []: list of column objects
    """
    if not table:
        return []
    return table.__table__.columns if hasattr(table, '__table__') else table.columns


def camel_case_split(s: str):
    return re.findall(r'[A-Z](?:[a-z]+|[A-Z]*(?=[A-Z]|$))', s)

def get_route_name(table) -> str:
    nm = table.__name__ if hasattr(table, '__name__') else table.__class__.__name__
    return '-'.join(list(map(lambda x: x.lower(), camel_case_split(nm))))

def get_typed_query_param(params: Union[MultiDict, Dict], name: str, out_type: Any=None):
    val = params.get(name)
    if isinstance(val, str):
        if out_type == list:
            return list(filter(None, map(lambda s: s.strip(), val.split(','))))
        
        if not out_type:
            if val.isdigit():
                return int(val)
            elif val.isdecimal():
                return float(val)
            elif val.lower() in ['true', 'false']:
                return val.lower() == 'true'
    
    try:
        return out_type(val)
    except:
        return val