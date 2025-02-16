from sqlalchemy import inspect
from sqlalchemy.orm import ColumnProperty
from sqlalchemy.engine.row import Row

def row_to_dict(row) -> dict:
    # return {key: getattr(row, key) for key in inspect(row).attrs.keys()}
    if isinstance(row, Row):
      return dict(row._mapping)
    else:
        result = {}
        for prop in inspect(row).mapper.iterate_properties:
            if isinstance(prop, ColumnProperty):
                result[prop.key] = getattr(row, prop.key)
        return result