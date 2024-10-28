from sqlalchemy.orm import sessionmaker

from ...infra.db import DBConfig, create_engine

engine = create_engine(DBConfig())
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    with SessionLocal() as db:
        yield db
