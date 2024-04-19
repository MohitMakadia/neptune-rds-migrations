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
        vertexIterate = iter(vertexIds)
        while True:
            try:
                vertexId = next(vertexIterate)
                # if validate_uuid(vertexId):
                Base.metadata.bind = self.engine
                messageValueMap = self.g.V(vertexId).valueMap().toList()[0]
                outEdges = self.g.V(vertexId).outE().toList()
                for edge in outEdges:
                    try:
                        session = createRdsSession()
                        message = Message(
                            message_id = vertexId,
                            content = messageValueMap.get("content", [None])[0],
                            last_login = messageValueMap.get("last_login", [None])[0],
                            seen = messageValueMap.get("seen", [None])[0],
                            sent_timestamp = messageValueMap.get("sent_timestamp", [None])[0],
                            authored_by = None,
                            addressed_to = None,
                            is_part_of = None
                        )
                        if edge.label == "authored_by":
                            message.authored_by = edge.id
                        elif edge.label == "addressed_to":
                            message.addressed_to = edge.id
                        elif edge.label == "is_part_of":
                            message.is_part_of = edge.id
                        
                        session.add(message)
                        commitRds(session)

                    except Exception as e:
                        print(f'Failed due to {str(e)}')
                # else:
                #     print(f'Invalid UUID Detected {vertexId} ... Skipping.')
            except StopIteration:
                break
                
currency = migrateMessage()
currency.migrateMessage()