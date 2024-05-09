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
        Base.metadata.bind = self.engine
        session = createRdsSession()
        vertexIds = [v.id for v in self.g.V().hasLabel("currency").toList()]
        try:
            for vertexId in vertexIds:
                currency_to_add = []
                currencyValueMap = self.g.V(vertexId).valueMap().toList()[0]
                outVertexs = self.g.V(vertexId).outE().toList()
                for outVertex in outVertexs:
                    out_vertex_id = str(outVertex).split("][")[1].split("->")[1][:-1]
                    try:
                        currency = Currency(
                            currency_id = vertexId,
                            code = currencyValueMap.get("code", [None])[0],
                            country = currencyValueMap.get("country", [None])[0],
                            last_login = currencyValueMap.get("last_login", [None])[0],
                            name = currencyValueMap.get("name", [None])[0],
                            is_currency_for = out_vertex_id
                        )
                        currency_to_add.append(currency)
                    
                    except Exception as e:
                        print(f'Failed due to {str(e)}')
                
                session.add_all(currency_to_add)
            session.commit()
        
        except Exception as e:
            print(str(e))
            session.rollback()
        
        finally:
            session.close()

currency = migrateCurrency()
currency.migrateCurrency()