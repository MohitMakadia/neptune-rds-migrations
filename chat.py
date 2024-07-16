# type: ignore[import]
from models.Chat import Chat, Base
from utils.connect import rds_connect, neptune_connect
from gremlin_python.structure.graph import Graph
from utils.session import create_rds_session
from utils.validation import check_if_table_exists


class MigrateChat:
    def __init__(self):
        self.engine = rds_connect()
        self.neptune_engine = neptune_connect()
        self.g = Graph().traversal().withRemote(self.neptune_engine)
        self.table = "Chat"

    def create_chat_table(self):
        print(f"Creating {self.table} Table ...")
        Chat.table_launch()
        print(f"{self.table} Table Created")

    def migrate_chat(self):
        check_if_table_exists(self.engine, self.table)
        self.create_chat_table()
        print(f"Starting Migration for {self.table} table ...")
        Base.metadata.bind = self.engine
        session = create_rds_session()
        vertex_ids = [v.id for v in self.g.V().hasLabel("chat").toList()]
        try:
            for vertex_id in vertex_ids:
                chats_to_add = []
                worker_id = None
                customer_id = None

                chat_value_map = self.g.V(vertex_id).valueMap().toList()[0]
                has_participant_vertex_ids = (
                    self.g.V(vertex_id).outE("has_participant").toList()
                )
                consists_of_vertex_ids = self.g.V(vertex_id).out("consists_of").toList()

                for has_participant_vertex_id in has_participant_vertex_ids:
                    out_vertex_id = (
                        str(has_participant_vertex_id)
                        .split("][")[1]
                        .split("->")[1][:-1]
                    )
                    if self.g.V(out_vertex_id).label().next() == "worker":
                        worker_id = out_vertex_id
                    if self.g.V(out_vertex_id).label().next() == "customer":
                        customer_id = out_vertex_id
                for consists_of_vertex_id in consists_of_vertex_ids:
                    try:
                        chat = Chat(
                            chat_id=vertex_id,
                            blocked=chat_value_map.get("blocked", [None])[0],
                            last_login=chat_value_map.get("last_login", [None])[0],
                            worker_id=worker_id,
                            customer_id=customer_id,
                            message_id=consists_of_vertex_id.id,
                            created_timestamp=chat_value_map.get(
                                "created_timestamp", [None]
                            )[0],
                        )
                        chats_to_add.append(chat)
                    except Exception as e:
                        print(f"Failed due to {str(e)}")
                session.add_all(chats_to_add)
            session.commit()

        except Exception as e:
            print(str(e))
            session.rollback()

        finally:
            session.close()


migrate_chat = MigrateChat()
migrate_chat.migrate_chat()
