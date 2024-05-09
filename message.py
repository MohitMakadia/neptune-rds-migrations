# type: ignore[import]
from models.Message import Message, Base
from utils.connect import rdsConnect, neptuneConnect
from gremlin_python.structure.graph import Graph
from utils.session import createRdsSession, commitRds
from utils.validation import validate_uuid, checkIfTableExists
 
class migrateMessage:

    def __init__(self):
        self.engine = rdsConnect()
        self.neptune_engine = neptuneConnect()
        self.g = Graph().traversal().withRemote(self.neptune_engine)
        self.table = "Message"

    def createCustomerTable(self):
        print(f'Creating {self.table} Table ...')
        Message.tableLaunch()
        print(f'{self.table} Table Created')

    def migrateMessage(self):
        checkIfTableExists(self.engine, self.table)
        self.createCustomerTable()
        print(f'Starting Migration for {self.table} table ...')
        vertexIds = [v.id for v in self.g.V().hasLabel("message").toList()]
        session = createRdsSession()
        try:
            for vertexId in vertexIds:
                message_to_add = []
                Base.metadata.bind = self.engine
                messageValueMap = self.g.V(vertexId).valueMap().toList()[0]
                outEdges = self.g.V(vertexId).outE().toList()
                
                customer_id = None
                worker_id = None
                chat_id = None
                author_id = None
                receiver_id = None
                
                for edge in outEdges:
                    
                    outVertexId = str(edge).split("][")[1].split("->")[1][:-1]
                    
                    if edge.label == "authored_by":
                        author_id = outVertexId
                    elif edge.label == "addressed_to":
                        receiver_id = outVertexId
                    
                    if self.g.V(outVertexId).label().next() == "customer":
                        customer_id = outVertexId
                    elif self.g.V(outVertexId).label().next() == "worker":
                        worker_id = outVertexId
                    elif edge.label == "is_part_of":
                        chat_id = outVertexId

                try:
                    
                    message = Message(
                        message_id = vertexId,
                        content = messageValueMap.get("content", [None])[0],
                        last_login = messageValueMap.get("last_login", [None])[0],
                        seen = messageValueMap.get("seen", [None])[0],
                        sent_timestamp = messageValueMap.get("sent_timestamp", [None])[0],
                        author_id = author_id,
                        receiver_id = receiver_id,
                        customer_id = customer_id,
                        worker_id = worker_id,
                        chat_id = chat_id
                    )
                    
                    message_to_add.append(message)
                        
                except Exception as e:
                    print(f'Failed due to {str(e)}')

                session.add_all(message_to_add)
            session.commit()

        except Exception as e:
            print(str(e))
            session.rollback()
        
        finally:
            session.close()
                        
currency = migrateMessage()
currency.migrateMessage()