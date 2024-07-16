# type: ignore[import]
from models.Payment import Payment, Base
from utils.connect import rds_connect, neptune_connect
from gremlin_python.structure.graph import Graph
from utils.session import create_rds_session
from utils.validation import check_if_table_exists


class migratePayment:

    def __init__(self):
        self.engine = rds_connect()
        self.neptune_engine = neptune_connect()
        self.g = Graph().traversal().withRemote(self.neptune_engine)
        self.table = "Payment"

    def create_payment_table(self):
        print(f"Creating {self.table} Table ...")
        Payment.table_launch()
        print(f"{self.table} Table Created")

    def migrate_payment(self):
        check_if_table_exists(self.engine, self.table)
        self.create_payment_table()
        print(f"Starting Migration for {self.table} table ...")
        vertex_ids = [v.id for v in self.g.V().hasLabel("payment").toList()]
        session = create_rds_session()
        try:
            for vertex_id in vertex_ids:
                payment_to_add = []
                Base.metadata.bind = self.engine
                payment_value_map = self.g.V(vertex_id).valueMap().toList()[0]
                out_vertexes = self.g.V(vertex_id).out().toList()
                for outVertex in out_vertexes:
                    try:
                        payment_to_add.append(
                            Payment(
                                id=vertex_id,
                                created_at=payment_value_map.get("created_at", [None])[
                                    0
                                ],
                                currency=payment_value_map.get("currency", [None])[0],
                                current_status=payment_value_map.get(
                                    "current_status", [None]
                                )[0],
                                last_login=payment_value_map.get("last_login", [None])[
                                    0
                                ],
                                latitude=payment_value_map.get("latitude", [None])[0],
                                longitude=payment_value_map.get("longitude", [None])[0],
                                place_id=payment_value_map.get("place_id", [None])[0],
                                updated_at=payment_value_map.get("updated_at", [None])[
                                    0
                                ],
                                value=payment_value_map.get("value", [None])[0],
                                issued_by=outVertex.id,
                                return_url=payment_value_map.get("return_url", [None])[
                                    0
                                ],
                            )
                        )
                    except Exception as e:
                        print(f"Failed due to {str(e)}")
                session.add_all(payment_to_add)
            session.commit()

        except Exception as e:
            print(str(e))
            session.rollback()

        finally:
            session.close()


currency = migratePayment()
currency.migrate_payment()
