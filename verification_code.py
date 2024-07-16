# type: ignore[import]
from models.Verification_Code import VerificationCode, Base
from utils.connect import rds_connect, neptune_connect
from gremlin_python.structure.graph import Graph
from utils.session import create_rds_session
from utils.validation import check_if_table_exists


class MigrateVerificationCode:

    def __init__(self):
        self.engine = rds_connect()
        self.neptune_engine = neptune_connect()
        self.g = Graph().traversal().withRemote(self.neptune_engine)
        self.table = "VerificationCode"

    def create_verification_code_table(self):
        print(f"Creating {self.table} Table ...")
        VerificationCode.table_launch()
        print(f"{self.table} Table Created")

    def migrate_verification_code(self):
        check_if_table_exists(self.engine, self.table)
        self.create_verification_code_table()
        print(f"Starting Migration for {self.table} table ...")
        Base.metadata.bind = self.engine
        session = create_rds_session()
        vertex_ids = [v.id for v in self.g.V().hasLabel("verification_code").toList()]
        for vertex_id in vertex_ids:
            verification_code_to_add = []
            verification_code_value_map = self.g.V(vertex_id).valueMap().toList()[0]
            try:
                verification_code = VerificationCode(
                    verificationcode_id=vertex_id,
                    active=verification_code_value_map.get("is_online", [None])[0],
                    created_timestamp=verification_code_value_map.get(
                        "created_timestamp", [None]
                    )[0],
                    person_id=verification_code_value_map.get("person_id", [None])[0],
                )
                verification_code_to_add.append(verification_code)
            except Exception as e:
                print(f"Failed due to {str(e)}")
            session.add_all(verification_code_to_add)
        session.commit()


migrate_review = MigrateVerificationCode()
migrate_review.migrate_verification_code()
