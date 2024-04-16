# type: ignore[import]
from models.Day import Day, Base
from utils.connect import rdsConnect, neptuneConnect
from gremlin_python.structure.graph import Graph
from utils.session import createRdsSession, commitRds
from utils.validation import validate_uuid, checkIfTableExists
 
class migrateDay:

    def __init__(self):
        self.engine = rdsConnect()
        self.neptune_engine = neptuneConnect()
        self.g = Graph().traversal().withRemote(self.neptune_engine)
        self.table = "Day"

    def createCustomerTable(self):
        print(f'Creating {self.table} Table ...')
        Day.tableLaunch()
        print(f'{self.table} Table Created')

    def migrateDay(self):
        checkIfTableExists(self.engine, self.table)
        self.createCustomerTable()
        print(f'Starting Migration for {self.table} table ...')
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
                            session = createRdsSession()
                            currency = Day(
                                day_id = vertexId,
                                day_name = daysValueMap.get("day_name", [""])[0],
                                day_of_week = daysValueMap.get("day_of_week", [-1])[0],
                                last_login = daysValueMap.get("last_login", [0])[0],
                                is_working_day_for = outVertex.id
                            )
                            session.add(currency)
                            commitRds(session)
                        except Exception as e:
                            print(f'Failed due to {str(e)}')
                else:
                    print(f'Invalid UUID Detected {vertexId} ... Skipping.')
            except StopIteration:
                break
                
currency = migrateDay()
currency.migrateDay()