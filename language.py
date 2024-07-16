# type: ignore[import]
from models.Language import Language
from utils.connect import rds_connect, neptune_connect
from gremlin_python.structure.graph import Graph
from sqlalchemy import inspect
from utils.session import create_rds_session, commit_rds


class MigrateLanguage:

    def __init__(self):
        self.engine = rds_connect()
        self.neptune_engine = neptune_connect()
        self.g = Graph().traversal().withRemote(self.neptune_engine)
        self.table = "Language"

    def check_if_table_exists(self):
        inspector = inspect(self.engine)
        if self.table in inspector.get_table_names():
            print(f"Table {self.table} exists.")
        else:
            print(f"Table {self.table} does not exist.")

    def create_language_table(self):
        print(f"Creating {self.table} Table ...")
        Language.table_launch()
        print(f"{self.table} Table Created")

    def migrate_language(self):
        self.check_if_table_exists()
        self.create_language_table()
        print(f"Starting Migration for {self.table} table ...")
        vertex_ids = self.g.V().hasLabel("language").toList()
        session = create_rds_session()
        for vertexId in vertex_ids:
            languages_to_add = []
            language_value_maps = self.g.V(vertexId).valueMap().toList()
            try:
                for language_value_map in language_value_maps:
                    out_vertexes = self.g.V(vertexId.id).out().toList()
                    for out_vertex in out_vertexes:
                        language = Language(
                            language_id=vertexId.id,
                            code=language_value_map.get("code", [None])[0],
                            last_login=language_value_map.get("last_login", [None])[0],
                            name=language_value_map.get("name", [None])[0],
                            spoken_by=out_vertex.id,
                        )
                        languages_to_add.append(language)
            except Exception as e:
                print(f"Error migrating verification with ID {vertexId}: {str(e)}")
            session.add_all(languages_to_add)
        session.commit()


migrate_language = MigrateLanguage()
migrate_language.migrate_language()
