# type: ignore[import]
from models.Currency import Currency, Base
from utils.connect import rdsConnect, neptuneConnect
from gremlin_python.structure.graph import Graph
from utils.session import createRdsSession, commitRds
from utils.validation import validate_uuid, checkIfTableExists
 
class migrateCurrency:

    def __init__(self):
        self.engine = rdsConnect()
        self.neptune_engine = neptuneConnect()
        self.g = Graph().traversal().withRemote(self.neptune_engine)
        self.table = "Currency"

    def createCustomerTable(self):
        print(f'Creating {self.table} Table ...')
        Currency.tableLaunch()
        print(f'{self.table} Table Created')

    def migrateCurrency(self):
        checkIfTableExists(self.engine, self.table)
        self.createCustomerTable()
        print(f'Starting Migration for {self.table} table ...')
        vertexIds = [v.id for v in self.g.V().hasLabel("currency").toList()]
        vertexIterate = iter(vertexIds)
        while True:
            try:
                vertexId = next(vertexIterate)
                #if validate_uuid(vertexId):
                Base.metadata.bind = self.engine
                currencyValueMap = self.g.V(vertexId).valueMap().toList()[0]
                outVertexs = self.g.V(vertexId).out().toList()
                for outVertex in outVertexs:
                    try:
                        session = createRdsSession()
                        currency = Currency(
                            currency_id = vertexId,
                            code = currencyValueMap.get("code", [None])[0],
                            country = currencyValueMap.get("country", [None])[0],
                            last_login = currencyValueMap.get("last_login", [None])[0],
                            name = currencyValueMap.get("name", [None])[0],
                            is_currency_for = outVertex.id
                        )
                        session.add(currency)
                        commitRds(session)
                    except Exception as e:
                        print(f'Failed due to {str(e)}')
                # else:
                #     print(f'Invalid UUID Detected {vertexId} ... Skipping.')
            except StopIteration:
                break
                
currency = migrateCurrency()
currency.migrateCurrency()