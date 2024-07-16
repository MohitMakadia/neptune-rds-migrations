# type: ignore[import]
from models.Currency import Currency, Base
from utils.connect import rds_connect, neptune_connect
from gremlin_python.structure.graph import Graph
from utils.session import create_rds_session
from utils.validation import check_if_table_exists


class migrateCurrency:

    def __init__(self):
        self.engine = rds_connect()
        self.neptune_engine = neptune_connect()
        self.g = Graph().traversal().withRemote(self.neptune_engine)
        self.table = "Currency"

    def create_customer_table(self):
        print(f"Creating {self.table} Table ...")
        Currency.table_launch()
        print(f"{self.table} Table Created")

    def migrate_currency(self):
        check_if_table_exists(self.engine, self.table)
        self.create_customer_table()
        print(f"Starting Migration for {self.table} table ...")
        Base.metadata.bind = self.engine
        session = create_rds_session()
        vertex_ids = [v.id for v in self.g.V().hasLabel("currency").toList()]
        try:
            for vertex_id in vertex_ids:
                currency_to_add = []
                currency_value_map = self.g.V(vertex_id).valueMap().toList()[0]
                out_vertexes = self.g.V(vertex_id).outE().toList()
                for out_vertex in out_vertexes:
                    out_vertex_id = str(out_vertex).split("][")[1].split("->")[1][:-1]
                    try:
                        currency_to_add.append(
                            Currency(
                                currency_id=vertex_id,
                                code=currency_value_map.get("code", [None])[0],
                                country=currency_value_map.get("country", [None])[0],
                                last_login=currency_value_map.get("last_login", [None])[
                                    0
                                ],
                                name=currency_value_map.get("name", [None])[0],
                                is_currency_for=out_vertex_id,
                            )
                        )
                    except Exception as e:
                        print(f"Failed due to {str(e)}")

                session.add_all(currency_to_add)
            session.commit()

        except Exception as e:
            print(str(e))
            session.rollback()

        finally:
            session.close()


currency = migrateCurrency()
currency.migrate_currency()
