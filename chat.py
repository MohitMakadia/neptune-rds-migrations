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
        Base.metadata.bind = self.engine
        session = createRdsSession()
        vertexIds = [v.id for v in self.g.V().hasLabel("chat").toList()]
        try:
            for vertexId in vertexIds:
                chats_to_add = []
                chatValueMap = self.g.V(vertexId).valueMap().toList()[0]
                has_participant_vertex_ids = self.g.V(vertexId).outE("has_participant").toList()
                consists_of_vertex_ids = self.g.V(vertexId).out("consists_of").toList()
                worker_id = None
                customer_id = None
                for has_participant_vertex_id in has_participant_vertex_ids:
 
                    out_vertex_id = str(has_participant_vertex_id).split("][")[1].split("->")[1][:-1]        
                    
                    if self.g.V(out_vertex_id).label().next() == "worker":
                        worker_id = out_vertex_id

                    if self.g.V(out_vertex_id).label().next() == "customer":
                        customer_id = out_vertex_id

                for consists_of_vertex_id in consists_of_vertex_ids:
                    try:
                        chat = Chat(
                            chat_id = vertexId,
                            blocked = chatValueMap.get("blocked", [None])[0],
                            last_login = chatValueMap.get("last_login", [None])[0],
                            has_participant_worker = worker_id,
                            has_participant_customer = customer_id,
                            consists_of = consists_of_vertex_id.id,
                            created_timestamp = chatValueMap.get("created_timestamp", [None])[0]
                        )
                        
                        chats_to_add.append(chat)
                        
                    except Exception as e:
                        print(f'Failed due to {str(e)}')
            
                session.add_all(chats_to_add)
            session.commit()
                    
        except Exception as e:
            print(str(e))
            session.rollback()
        
        finally:
            session.close()

migrate_chat = MigrateChat()
migrate_chat.migrateChat()
