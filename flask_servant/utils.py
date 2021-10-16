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

def get_route_name(table) -> str:
    nm = table.__name__ if hasattr(table, '__name__') else table.__class__.__name__