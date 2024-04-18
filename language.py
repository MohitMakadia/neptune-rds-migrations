# type: ignore[import]
from models.Language import Language 
from utils.connect import rdsConnect, neptuneConnect
from gremlin_python.structure.graph import Graph
from sqlalchemy import inspect
from utils.session import createRdsSession, commitRds
from utils.validation import validate_uuid

class MigrateLanguage:
    
    def __init__(self):
        self.engine = rdsConnect()
        self.neptune_engine = neptuneConnect()
        self.g = Graph().traversal().withRemote(self.neptune_engine)
        self.table = "Language"

    def checkIfTableExists(self):
        inspector = inspect(self.engine)
        if self.table in inspector.get_table_names():
            print(f'Table {self.table} exists.')
        else:
            print(f'Table {self.table} does not exist.')

    def createLanguageTable(self):
        print(f'Creating {self.table} Table ...')
        Language.tableLaunch()
        print(f'{self.table} Table Created')

    def migratelanguage(self):
        self.checkIfTableExists()
        self.createLanguageTable()
        print(f'Starting Migration for {self.table} table ...')
        
        vertexIds = self.g.V().hasLabel("language").toList()
        for vertexId in vertexIds:
            session = createRdsSession()
            # if validate_uuid(vertexId.id):
            languageValueMaps = self.g.V(vertexId).valueMap().toList()
            try:                        
                for languageValueMap in languageValueMaps:
                    outVertexs = self.g.V(vertexId.id).out().toList()
                    for outVertex in outVertexs:
                        language = Language(
                            language_id=vertexId.id,
                            code=languageValueMap.get("code", [None])[0],
                            last_login=languageValueMap.get("last_login", [None])[0],
                            name=languageValueMap.get("name", [None])[0],
                            spoken_by=outVertex.id,
                        )
                        
                        session.add(language)
                        commitRds(session)
            except Exception as e:
                print(f"Error migrating verification with ID {vertexId}: {str(e)}")
            # else:
            #     print(f'Invalid UUID Detected {vertexId} ... Skipping.')

migrate_language = MigrateLanguage()
migrate_language.migratelanguage() 