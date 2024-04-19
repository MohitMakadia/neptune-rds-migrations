# type: ignore[import]
from models.Chat import Chat, Base
from utils.connect import rdsConnect, neptuneConnect
from gremlin_python.structure.graph import Graph
from utils.session import createRdsSession, commitRds
from utils.validation import validate_uuid, checkIfTableExists

class MigrateChat:
    def __init__(self):
        self.engine = rdsConnect()
        self.neptune_engine = neptuneConnect()
        self.g = Graph().traversal().withRemote(self.neptune_engine)
        self.table = "Chat"

    def createChatTable(self):
        print(f'Creating {self.table} Table ...')
        Chat.tableLaunch()
        print(f'{self.table} Table Created')

    def migrateChat(self):
        checkIfTableExists(self.engine, self.table)
        self.createChatTable()
        print(f'Starting Migration for {self.table} table ...')

        vertexIds = [v.id for v in self.g.V().hasLabel("chat").toList()]
        vertexIterate = iter(vertexIds)

        while True:
            try:
                vertexId = next(vertexIterate)
                #if validate_uuid(vertexId):
                Base.metadata.bind = self.engine
                chatValueMap = self.g.V(vertexId).valueMap().toList()[0]

                # Query for has_participant vertex
                has_participant_vertex = self.g.V(vertexId).out("has_participant").next()
                has_participant_id = has_participant_vertex.id if has_participant_vertex is not None else None

                # Query for consists_of vertex
                consists_of_vertex = self.g.V(vertexId).out("consists_of").next()
                consists_of_id = consists_of_vertex.id if consists_of_vertex is not None else None

                try:
                    session = createRdsSession()
                    chat = Chat(
                        chat_id = vertexId,
                        blocked = chatValueMap.get("blocked", [None])[0],
                        last_login = chatValueMap.get("last_login", [None])[0],
                        has_participant = has_participant_id,
                        consists_of = consists_of_id,
                        created_timestamp = chatValueMap.get("created_timestamp", [None])[0]
                    )
                    
                    session.add(chat)
                    commitRds(session)
                
                except Exception as e:
                    print(f'Failed due to {str(e)}')
                # else:
                #     print(f'Invalid UUID Detected {vertexId} ... Skipping.')
            except StopIteration:
                break

migrate_chat = MigrateChat()
migrate_chat.migrateChat()
