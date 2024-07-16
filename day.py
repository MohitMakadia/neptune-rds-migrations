# type: ignore[import]
from models.Day import Day, Base
from utils.connect import rds_connect, neptune_connect
from gremlin_python.structure.graph import Graph
from utils.session import create_rds_session, commit_rds
from utils.validation import validate_uuid, check_if_table_exists


class migrateDay:

    def __init__(self):
        self.engine = rds_connect()
        self.neptune_engine = neptune_connect()
        self.g = Graph().traversal().withRemote(self.neptune_engine)
        self.table = "Day"

    def createCustomerTable(self):
        print(f"Creating {self.table} Table ...")
        Day.table_launch()
        print(f"{self.table} Table Created")

    def migrateDay(self):
        check_if_table_exists(self.engine, self.table)
        self.createCustomerTable()
        print(f"Starting Migration for {self.table} table ...")
        vertexIds = [v.id for v in self.g.V().hasLabel("day").toList()]
        vertexIterate = iter(vertexIds)
        while True:
            try:
                vertexId = next(vertexIterate)
                if validate_uuid(vertexId):
                    Base.metadata.bind = self.engine
                    daysValueMap = self.g.V(vertexId).valueMap().toList()[0]
                    outVertexs = self.g.V(vertexId).out().toList()
                    for outVertex in outVertexs:
                        try:
                            session = create_rds_session()
                            currency = Day(
                                day_id=vertexId,
                                day_name=daysValueMap.get("day_name", [None])[0],
                                day_of_week=daysValueMap.get("day_of_week", [None])[0],
                                last_login=daysValueMap.get("last_login", [None])[0],
                                is_available_for=outVertex.id,
                            )
                            session.add(currency)
                            commit_rds(session)
                        except Exception as e:
                            print(f"Failed due to {str(e)}")
                else:
                    print(f"Invalid UUID Detected {vertexId} ... Skipping.")
            except StopIteration:
                break


currency = migrateDay()
currency.migrateDay()
