import uuid
from sqlalchemy import inspect


def validate_uuid(uuid_str):
    try:
        uuid.UUID(uuid_str)
        return True
    except ValueError:
        return False


def check_if_table_exists(engine, table_name):
    inspector = inspect(engine)
    if table_name in inspector.get_table_names():
        print(f"Table {table_name} exists.")
    else:
        print(f"Table {table_name} does not exist.")
