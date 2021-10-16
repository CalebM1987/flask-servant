from typing import TypeVar
from flask_servant.declarative import db
import sqlalchemy

Column = sqlalchemy.sql.schema.Column
InstrumentedAttribute = sqlalchemy.orm.attributes.InstrumentedAttribute

def query_table(table, session=None, **kwargs):
    session = session or db.session

    conditions = []
    for kwarg, val in kwargs.items():
        # check for like query
        base = kwarg
        hasWildcard = kwarg.endswith('.$like')
        if hasWildcard:
            base = kwarg.split('.')[0]
        if hasattr(table, base):
            col = getattr(table, base)
            if hasWildcard:
                conditions.append(col.ilike(f'%{val}%'))
            else:
                conditions.append(col == val)
    print('table has query: ', hasattr(table.__table__, 'query'))
    if hasattr(table, 'query'):
        res = table.query.filter(*conditions)
    else:
        res = session.query(table).filter(*conditions)
    
    return res.all()
