from sqlalchemy import JSON
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    type_annotation_map = {
        dict[str, str]: JSON,
    }

    __mapper_args__ = {"eager_defaults": True}
