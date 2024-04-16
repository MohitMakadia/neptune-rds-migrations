# type: ignore[import]
from models.Payment import Payment, Base
from utils.connect import rdsConnect, neptuneConnect
from gremlin_python.structure.graph import Graph
from utils.session import createRdsSession, commitRds
from utils.validation import validate_uuid, checkIfTableExists
 
class migratePayment:

    def __init__(self):
        self.engine = rdsConnect()
        self.neptune_engine = neptuneConnect()
        self.g = Graph().traversal().withRemote(self.neptune_engine)
        self.table = "Payment"

    def createCustomerTable(self):
        print(f'Creating {self.table} Table ...')
        Payment.tableLaunch()
        print(f'{self.table} Table Created')

    def migratePayment(self):
        checkIfTableExists(self.engine, self.table)
        self.createCustomerTable()
        print(f'Starting Migration for {self.table} table ...')
        vertexIds = [v.id for v in self.g.V().hasLabel("payment").toList()]
        vertexIterate = iter(vertexIds)
        while True:
            try:
                vertexId = next(vertexIterate)         
                Base.metadata.bind = self.engine
                paymentValueMap = self.g.V(vertexId).valueMap().toList()[0]
                outVertexs = self.g.V(vertexId).out().toList()
                for outVertex in outVertexs:
                    try:
                        session = createRdsSession()
                        payment = Payment(
                            id = vertexId,
                            created_at = paymentValueMap.get("created_at", [None])[0],
                            currency = paymentValueMap.get("currency", [None])[0],
                            current_status = paymentValueMap.get("current_status", [None])[0],
                            last_login = paymentValueMap.get("last_login", [None])[0],
                            latitude = paymentValueMap.get("latitude", [None])[0],
                            longitute = paymentValueMap.get("longitude", [None])[0],
                            place_id = paymentValueMap.get("place_id", [None])[0],
                            updated_at = paymentValueMap.get("updated_at", [None])[0],
                            value = paymentValueMap.get("value", [None])[0],
                            issued_by = outVertex.id
                        )

                        session.add(payment)
                        commitRds(session)

                    except Exception as e:
                        print(f'Failed due to {str(e)}')  
            except StopIteration:
                break
                
currency = migratePayment()
currency.migratePayment()