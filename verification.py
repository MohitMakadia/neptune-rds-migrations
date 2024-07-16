# type: ignore[import]
from models.Verification import Verification
from utils.connect import rds_connect, neptune_connect
from gremlin_python.structure.graph import Graph
from utils.session import create_rds_session
from utils.validation import check_if_table_exists


class MigrateVerification:

    def __init__(self):
        self.engine = rds_connect()
        self.neptune_engine = neptune_connect()
        self.g = Graph().traversal().withRemote(self.neptune_engine)
        self.table = "Verification"

    def create_verification_table(self):
        print(f"Creating {self.table} Table ...")
        Verification.table_launch()
        print(f"{self.table} Table Created")

    def migrate_verification(self):
        check_if_table_exists(self.engine, self.table)
        self.create_verification_table()
        print(f"Starting Migration for {self.table} table ...")

        with create_rds_session() as session:
            vertex_ids = self.g.V().hasLabel("verification").toList()
            for vertex_id in vertex_ids:
                workers_to_add = []
                verification_value_maps = self.g.V(vertex_id).valueMap().toList()
                try:
                    for verification_value_map in verification_value_maps:
                        out_vertexes = self.g.V(vertex_id.id).out().toList()
                        for outVertex in out_vertexes:
                            verification = Verification(
                                last_login=verification_value_map.get(
                                    "last_login", [None]
                                )[0],
                                type=verification_value_map.get("type", [None])[0],
                                used_to_verify=outVertex.id,
                                verification_id=vertex_id.id,
                            )
                            workers_to_add.append(verification)
                        session.add_all(workers_to_add)
                except Exception as e:
                    print(f"Error migrating verification with ID {vertex_id}: {str(e)}")
            session.commit()


migrate_verification = MigrateVerification()
migrate_verification.migrate_verification()
