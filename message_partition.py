# type: ignore[import]
from models.Message import Message, Base
from utils.connect import rds_connect, neptune_connect
from gremlin_python.structure.graph import Graph
from utils.session import create_rds_session
from utils.validation import check_if_table_exists
import sys
import ast
import os


def process_chunks(key):
    input_file = "message.txt"
    with open("chunks/" + input_file, "r") as f:
        chunks_str = f.read()

    chunks = ast.literal_eval(chunks_str)
    for k, v in chunks.items():
        if k == key:
            return k, v

    return None, None


def mark_chunk_completed(chunk_num, status):

    chunks_folder = "chunks/message_status"
    if not os.path.exists(chunks_folder):
        os.makedirs(chunks_folder)

    completed_file = f"chunks/message_status/completed_{chunk_num}.txt"

    with open(completed_file, "w") as f:
        f.write(str({chunk_num: [status]}))


class migrateMessage:

    def __init__(self, chunk_number):
        self.engine = rds_connect()
        self.neptune_engine = neptune_connect()
        self.g = Graph().traversal().withRemote(self.neptune_engine)
        self.table = "Message"
        self.chunk_number = chunk_number

    def create_message_table(self):
        print(f"Creating {self.table} Table ...")
        Message.table_launch()
        print(f"{self.table} Table Created")

    def migrate_message(self):
        check_if_table_exists(self.engine, self.table)
        self.create_message_table()
        print(f"Starting Migration for {self.table} table ...")
        chunk_name, chunk_data = process_chunks(self.chunk_number)
        print("Chunk -> ", chunk_name)
        session = create_rds_session()
        try:
            for vertex_id in chunk_data:
                message_to_add = []
                Base.metadata.bind = self.engine
                message_value_map = self.g.V(vertex_id).valueMap().toList()[0]
                out_edges = self.g.V(vertex_id).outE().toList()

                customer_id = None
                worker_id = None
                chat_id = None
                author_id = None
                receiver_id = None

                for edge in out_edges:

                    out_vertex_id = str(edge).split("][")[1].split("->")[1][:-1]

                    if edge.label == "authored_by":
                        author_id = out_vertex_id
                    elif edge.label == "addressed_to":
                        receiver_id = out_vertex_id

                    if self.g.V(out_vertex_id).label().next() == "customer":
                        customer_id = out_vertex_id
                    elif self.g.V(out_vertex_id).label().next() == "worker":
                        worker_id = out_vertex_id
                    elif edge.label == "is_part_of":
                        chat_id = out_vertex_id

                try:

                    message = Message(
                        message_id=vertex_id,
                        content=message_value_map.get("content", [None])[0],
                        last_login=message_value_map.get("last_login", [None])[0],
                        seen=message_value_map.get("seen", [None])[0],
                        sent_timestamp=message_value_map.get("sent_timestamp", [None])[
                            0
                        ],
                        author_id=author_id,
                        receiver_id=receiver_id,
                        customer_id=customer_id,
                        worker_id=worker_id,
                        chat_id=chat_id,
                    )

                    message_to_add.append(message)

                except Exception as e:
                    print(f"Failed due to {str(e)}")

                session.add_all(message_to_add)
            session.commit()

        except Exception as e:
            print(str(e))
            session.rollback()

        finally:
            session.close()

        mark_chunk_completed(chunk_name, "Completed")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 message_partition.py <chunk_number>")
        sys.exit(1)

    chunk_number = int(sys.argv[1])
    currency = migrateMessage(chunk_number)
    currency.migrate_message()
