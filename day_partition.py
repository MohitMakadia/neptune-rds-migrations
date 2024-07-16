# type: ignore[import]
from models.Day import Day, Base
from utils.connect import rds_connect, neptune_connect
from gremlin_python.structure.graph import Graph
from utils.session import create_rds_session
from utils.validation import check_if_table_exists
import ast
import os
import sys


class migrateDay:

    def __init__(self, chunk_number):
        self.engine = rds_connect()
        self.neptune_engine = neptune_connect()
        self.g = Graph().traversal().withRemote(self.neptune_engine)
        self.table = "Day"
        self.chunk_number = chunk_number

    def create_day_table(self):
        print(f"Creating {self.table} Table ...")
        Day.table_launch()
        print(f"{self.table} Table Created")

    @staticmethod
    def process_chunks(key):
        input_file = "day.txt"
        with open("chunks/" + input_file, "r") as f:
            chunks_str = f.read()

        chunks = ast.literal_eval(chunks_str)
        for k, v in chunks.items():
            if k == key:
                return k, v

        return None, None

    @staticmethod
    def mark_chunk_completed(chunk_num, status):

        chunks_folder = "chunks/day_status"
        if not os.path.exists(chunks_folder):
            os.makedirs(chunks_folder)

        completed_file = f"chunks/day_status/completed_{chunk_num}.txt"

        with open(completed_file, "w") as f:
            f.write(str({chunk_num: [status]}))

    def migrate_day(self):
        check_if_table_exists(self.engine, self.table)
        self.create_day_table()
        print(f"Starting Migration for {self.table} table ...")
        Base.metadata.bind = self.engine
        chunk_name, chunk_data = self.process_chunks(chunk_number)
        print("Chunk -> ", chunk_name)
        session = create_rds_session()
        try:
            for vertexId in chunk_data:
                days_to_add = []
                days_value_map = self.g.V(vertexId).valueMap().toList()[0]
                out_vertexes = self.g.V(vertexId).outE().toList()
                for outVertex in out_vertexes:
                    try:
                        out_vertex_id = (
                            str(outVertex).split("][")[1].split("->")[1][:-1]
                        )
                        days_to_add.append(
                            Day(
                                day_id=vertexId,
                                day_name=days_value_map.get("day_name", [None])[0],
                                day_of_week=days_value_map.get("day_of_week", [None])[
                                    0
                                ],
                                last_login=days_value_map.get("last_login", [None])[0],
                                is_available_for=out_vertex_id,
                            )
                        )

                    except Exception as e:
                        print(f"Failed due to {str(e)}")

                session.add_all(days_to_add)
            session.commit()

        except Exception as e:
            print(str(e))
            session.rollback()

        finally:
            session.close()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 day_partition.py <chunk_number>")
        sys.exit(1)

    chunk_number = int(sys.argv[1])
    day = migrateDay(chunk_number)
    day.migrate_day()
