# type: ignore[import]
from models.Worker import Worker, Base
from utils.connect import rds_connect, neptune_connect
from gremlin_python.structure.graph import Graph
from utils.session import create_rds_session
from utils.validation import check_if_table_exists
import ast
import os
import sys


def process_chunks(key):
    input_file = "worker.txt"
    with open("chunks/" + input_file, "r") as f:
        chunks_str = f.read()

    chunks = ast.literal_eval(chunks_str)
    for k, v in chunks.items():
        if k == key:
            return k, v

    return None, None


def mark_chunk_completed(chunk_num, status):

    chunks_folder = "chunks/worker_status"
    if not os.path.exists(chunks_folder):
        os.makedirs(chunks_folder)

    completed_file = f"chunks/worker_status/completed_{chunk_num}.txt"

    with open(completed_file, "w") as f:
        f.write(str({chunk_num: [status]}))


class migrateWorker:

    def __init__(self, chunk_number):
        self.engine = rds_connect()
        self.neptune_engine = neptune_connect()
        self.g = Graph().traversal().withRemote(self.neptune_engine)
        self.table = "Worker"
        self.chunk_number = chunk_number

    def create_worker_table(self):
        print(f"Creating {self.table} Table ...")
        Worker.table_launch()
        print(f"{self.table} Table Created")

    def migrate_worker(self):
        check_if_table_exists(self.engine, self.table)
        self.create_worker_table()
        print(f"Starting Migration for {self.table} table ...")
        Base.metadata.bind = self.engine
        chunk_name, chunk_data = process_chunks(self.chunk_number)
        print("Chunk -> ", chunk_name)
        session = create_rds_session()
        try:
            for vertexId in chunk_data:
                workers_to_add = []
                worker_value_map = self.g.V(vertexId).valueMap().toList()[0]
                try:
                    workers_to_add.append(
                        Worker(
                            worker_id=vertexId,
                            amount=worker_value_map.get("amount", [None])[0],
                            domain_language=worker_value_map.get(
                                "domain_language", [None]
                            )[0],
                            domain=worker_value_map.get("domain", [None])[0],
                            email=worker_value_map.get("email", [None])[0],
                            experience=worker_value_map.get("experience", [None])[0],
                            first_name=worker_value_map.get("first_name", [None])[0],
                            internal_score=worker_value_map.get(
                                "internal_score", [None]
                            )[0],
                            is_online=worker_value_map.get("is_online", [False])[0],
                            is_suspended=worker_value_map.get("is_suspended", [False])[
                                0
                            ],
                            is_deleted=worker_value_map.get("is_deleted", [False])[0],
                            last_login=worker_value_map.get("last_login", [None])[0],
                            location_address=worker_value_map.get(
                                "location_address", [None]
                            )[0],
                            location_city=worker_value_map.get("location_city", [None])[
                                0
                            ],
                            location_country=worker_value_map.get(
                                "location_country", [None]
                            )[0],
                            location_longitude=worker_value_map.get(
                                "location_longitude", [None]
                            )[0],
                            location_latitude=worker_value_map.get(
                                "location_latitude", [None]
                            )[0],
                            location_place_id=worker_value_map.get(
                                "location_place_id", [None]
                            )[0],
                            location_slug=worker_value_map.get("location_slug", [None])[
                                0
                            ],
                            location_country_code=worker_value_map.get(
                                "location_country_code", [None]
                            )[0],
                            max_distance=worker_value_map.get("max_distance", [None])[
                                0
                            ],
                            personal_note=worker_value_map.get("personal_note", [None])[
                                0
                            ],
                            profile_picture=worker_value_map.get(
                                "profile_picture", [None]
                            )[0],
                            published=worker_value_map.get("published", [False])[0],
                            registered_date=worker_value_map.get(
                                "registered_date", [None]
                            )[0],
                            score=worker_value_map.get("score", [None])[0],
                            user_alert=worker_value_map.get("user_alert", [False])[0],
                            votes=worker_value_map.get("votes", [None])[0],
                        )
                    )
                except Exception as e:
                    print(str(e))

                session.add_all(workers_to_add)
            session.commit()

        except Exception as e:
            print(str(e))
            session.rollback()

        finally:
            session.close()

        mark_chunk_completed(chunk_name, "Completed")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 worker_partition.py <chunk_number>")
        sys.exit(1)

    chunk_number = int(sys.argv[1])
    worker = migrateWorker(chunk_number)
    worker.migrate_worker()
