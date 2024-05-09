# type: ignore[import]
from models.Payment import Payment, Base
from utils.connect import rdsConnect, neptuneConnect
from gremlin_python.structure.graph import Graph
from utils.session import createRdsSession
from utils.validation import checkIfTableExists
 
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
        session = createRdsSession()
        try:
            for vertexId in vertexIds: 
                payment_to_add = []       
                Base.metadata.bind = self.engine
                paymentValueMap = self.g.V(vertexId).valueMap().toList()[0]
                outVertexs = self.g.V(vertexId).out().toList()
                for outVertex in outVertexs:
                    try:
                        payment = Payment(
                            id = vertexId,
                            created_at = paymentValueMap.get("created_at", [None])[0],
                            currency = paymentValueMap.get("currency", [None])[0],
                            current_status = paymentValueMap.get("current_status", [None])[0],
                            last_login = paymentValueMap.get("last_login", [None])[0],
                            latitude = paymentValueMap.get("latitude", [None])[0],
                            longitude = paymentValueMap.get("longitude", [None])[0],
                            place_id = paymentValueMap.get("place_id", [None])[0],
                            updated_at = paymentValueMap.get("updated_at", [None])[0],
                            value = paymentValueMap.get("value", [None])[0],
                            issued_by = outVertex.id,
                            return_url = paymentValueMap.get("return_url", [None])[0]
                        )

                        payment_to_add.append(payment)
                    except Exception as e:
                        print(f'Failed due to {str(e)}')  
                session.add_all(payment_to_add)
            session.commit()

        except Exception as e:
            print(str(e))
            session.rollback()
        
        finally:
            session.close()
            
currency = migratePayment()
currency.migratePayment()