import importlib
import inspect
from pathlib import Path

from atlas_provider_sqlalchemy.ddl import print_ddl  # type: ignore[import-untyped]

from src.infra import orm

models = []

orm_path = Path(orm.__file__).parent

for script in orm_path.glob("*.py"):
    if script.suffix == ".py" and script.stem not in ["__init__", "base"]:
        module_name = f"{orm.__name__}.{script.stem}"
        module = importlib.import_module(module_name)

        for name, obj in inspect.getmembers(module):
            if inspect.isclass(obj) and obj != orm.base.Base and issubclass(obj, orm.base.Base):
                models.append(obj)

print_ddl("postgresql", models)
