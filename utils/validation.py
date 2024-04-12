import uuid
from sqlalchemy import inspect

def validate_uuid(uuid_str):
    try:
        uuid.UUID(uuid_str)
        return True
    except ValueError:
        return False
    
def checkIfTableExists(engine, tableName):
    inspector = inspect(engine)
    if tableName in inspector.get_table_names():
        print(f'Table {tableName} exists.')
    else:
        print(f'Table {tableName} does not exist.')
