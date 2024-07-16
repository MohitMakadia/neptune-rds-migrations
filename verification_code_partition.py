# type: ignore[import]
from models.Verification_Code import VerificationCode, Base
from utils.connect import rds_connect, neptune_connect
from gremlin_python.structure.graph import Graph
from utils.session import create_rds_session
from utils.validation import check_if_table_exists
import sys
import ast
import os


def process_chunks(key):
    input_file = "verification_code.txt"
    with open("chunks/" + input_file, "r") as f:
        chunks_str = f.read()

    chunks = ast.literal_eval(chunks_str)
    for k, v in chunks.items():
        if k == key:
            return k, v

    return None, None


def mark_chunk_completed(chunk_num, status):

    chunks_folder = "chunks/verification_code_status"
    if not os.path.exists(chunks_folder):
        os.makedirs(chunks_folder)

    completed_file = f"chunks/verification_code_status/completed_{chunk_num}.txt"

    with open(completed_file, "w") as f:
        f.write(str({chunk_num: [status]}))


class MigrateVerificationCode:

    def __init__(self, chunk_number):
        self.engine = rds_connect()
        self.neptune_engine = neptune_connect()
        self.g = Graph().traversal().withRemote(self.neptune_engine)
        self.table = "VerificationCode"
        self.chunk_number = chunk_number

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
        # vertex_ids = [v.id for v in self.g.V().hasLabel("verification_code").toList()]
        chunk_name, chunk_data = process_chunks(self.chunk_number)
        print("Chunk -> ", chunk_name)
        try:
            for vertex_id in chunk_data:
                verification_code_to_add = []
                verification_code_value_map = self.g.V(vertex_id).valueMap().toList()[0]
                try:
                    verification_code = VerificationCode(
                        verificationcode_id=vertex_id,
                        active=verification_code_value_map.get("is_online", [None])[0],
                        created_timestamp=verification_code_value_map.get(
                            "created_timestamp", [None]
                        )[0],
                        person_id=verification_code_value_map.get("person_id", [None])[
                            0
                        ],
                    )
                    verification_code_to_add.append(verification_code)
                except Exception as e:
                    print(f"Failed due to {str(e)}")
                session.add_all(verification_code_to_add)
            session.commit()

        except Exception as e:
            print(str(e))
            session.rollback()

        finally:
            session.close()

        mark_chunk_completed(chunk_name, "Completed")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 verification_code_partition.py <chunk_number>")
        sys.exit(1)

    chunk_number = int(sys.argv[1])
    migrate_review = MigrateVerificationCode(chunk_number)
    migrate_review.migrate_verification_code()
