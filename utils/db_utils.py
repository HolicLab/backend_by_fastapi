from sqlalchemy import inspect
from sqlalchemy.orm import ColumnProperty
from sqlalchemy.engine.row import Row
from datetime import datetime

def row_to_dict(row) -> dict:
    if isinstance(row, Row):
        # Row 객체인 경우 (result set에서 바로 가져온 경우)
        return {
            key: value.isoformat() if isinstance(value, datetime) else value
            for key, value in row._mapping.items()
        }
    else:
        # SQLAlchemy 모델 인스턴스인 경우
        result = {}
        for prop in inspect(row).mapper.iterate_properties:
            if isinstance(prop, ColumnProperty):
                value = getattr(row, prop.key)
                if isinstance(value, datetime):
                    result[prop.key] = value.isoformat()  # 명시적 ISO 8601 변환
                else:
                    result[prop.key] = value
        return result