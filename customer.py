# type: ignore[import]
from models.Customer import Customer, Base
from utils.connect import rds_connect, neptune_connect
from gremlin_python.structure.graph import Graph
from utils.session import create_rds_session
from utils.validation import check_if_table_exists
import sys
import ast
import os


def mark_chunk_completed(chunk_num, status):

    chunks_folder = "chunks/customer_status"
    if not os.path.exists(chunks_folder):
        os.makedirs(chunks_folder)

    completed_file = f"chunks/customer_status/completed_{chunk_num}.txt"

    with open(completed_file, "w") as f:
        f.write(str({chunk_num: [status]}))


def process_chunks(key):
    input_file = "customer.txt"
    with open("chunks/" + input_file, "r") as f:
        chunks_str = f.read()

    chunks = ast.literal_eval(chunks_str)
    for k, v in chunks.items():
        if k == key:
            return k, v

    return None, None


class migrateCustomer:

    def __init__(self, chunk_number):
        self.engine = rds_connect()
        self.neptune_engine = neptune_connect()
        self.g = Graph().traversal().withRemote(self.neptune_engine)
        self.table = "Customer1"
        self.chunk_number = chunk_number

    def create_customer_table(self):
        print(f"Creating {self.table} Table ...")
        Customer.table_launch()
        print(f"{self.table} Table Created")

    def migrate_customer(self):
        check_if_table_exists(self.engine, self.table)
        self.create_customer_table()
        print(f"Starting Migration for {self.table} table ...")
        Base.metadata.bind = self.engine
        chunk_name, chunk_data = process_chunks(self.chunk_number)
        session = create_rds_session()
        for vertexId in chunk_data:
            customer_value_map = self.g.V(vertexId).valueMap().toList()[0]
            try:
                session.add(
                    Customer(
                        # customer_id=vertexId,  # vertexId.id
                        id=vertexId,
                        amount=customer_value_map.get("amount", [None])[0],
                        domain_language=customer_value_map.get(
                            "domain_language", [None]
                        )[0],
                        domain=customer_value_map.get("domain", [None])[0],
                        duration=customer_value_map.get("duration", [None])[0],
                        email=customer_value_map.get("email", [None])[0],
                        experience=customer_value_map.get("experience", [None])[0],
                        first_name=customer_value_map.get("first_name", [None])[0],
                        internal_score=customer_value_map.get("internal_score", [None])[
                            0
                        ],
                        interval=customer_value_map.get("interval", [None])[0],
                        is_deleted=customer_value_map.get("is_deleted", [None])[0],
                        is_online=customer_value_map.get("is_online", [None])[0],
                        is_suspended=customer_value_map.get("is_suspended", [None])[0],
                        last_login=customer_value_map.get("last_login", [None])[0],
                        location_address=customer_value_map.get(
                            "location_address", [None]
                        )[0],
                        location_city=customer_value_map.get("location_city", [None])[
                            0
                        ],
                        location_country=customer_value_map.get(
                            "location_country", [None]
                        )[0],
                        location_place_id=customer_value_map.get(
                            "location_place_id", [None]
                        )[0],
                        location_slug=customer_value_map.get("location_slug", [None])[
                            0
                        ],
                        location_country_code=customer_value_map.get(
                            "location_country_code", [None]
                        )[0],
                        personal_note=customer_value_map.get("personal_note", [None])[
                            0
                        ],
                        phone_no=customer_value_map.get("phone_no", [None])[0],
                        profile_picture=customer_value_map.get(
                            "profile_picture", [None]
                        )[0],
                        published=customer_value_map.get("published", [None])[0],
                        registered_date=customer_value_map.get(
                            "registered_date", [None]
                        )[0],
                        score=customer_value_map.get("score", [None])[0],
                        user_alert=customer_value_map.get("user_alert", [None])[0],
                        votes=customer_value_map.get("votes", [None])[0],
                        location_longitude=customer_value_map.get(
                            "location_longitude", [None]
                        )[0],
                        location_latitude=customer_value_map.get(
                            "location_latitude", [None]
                        )[0],
                        max_distance=customer_value_map.get("max_distance", [None])[0],
                    )
                )
                session.commit()

            except Exception as e:
                print(f"Failed due to {str(e)}")
                session.rollback()

        mark_chunk_completed(chunk_name, "Completed")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 customer.py <chunk_number>")
        sys.exit(1)

    chunk_number = int(sys.argv[1])
    customer = migrateCustomer(chunk_number)
    customer.migrate_customer()
