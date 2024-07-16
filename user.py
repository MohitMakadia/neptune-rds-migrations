# type: ignore[import]
from models.User import User, Base
from utils.connect import rds_connect, neptune_connect
from gremlin_python.structure.graph import Graph
from utils.session import create_rds_session, commit_rds
from utils.validation import check_if_table_exists


class MigrateUser:
    def __init__(self):
        self.engine = rds_connect()
        self.neptune_engine = neptune_connect()
        self.g = Graph().traversal().withRemote(self.neptune_engine)
        self.table = "User"

    def createUserTable(self):
        print(f"Creating {self.table} Table ...")
        User.table_launch()
        print(f"{self.table} Table Created")

    def migrateUser(self):
        check_if_table_exists(self.engine, self.table)
        self.createUserTable()
        print(f"Starting Migration for {self.table} table ...")

        vertexIds = [v.id for v in self.g.V().hasLabel("user").toList()]
        vertexIterate = iter(vertexIds)

        while True:
            try:
                vertexId = next(vertexIterate)

                Base.metadata.bind = self.engine

                favors_vertex = self.g.V(vertexId).out("favors").next()
                favors_id = favors_vertex.id if favors_vertex is not None else None

                try:
                    session = create_rds_session()
                    user = User(
                        user_id=vertexId,
                        favors=favors_id,
                    )
                    session.add(user)
                    commit_rds(session)

                except Exception as e:
                    print(f"Failed due to {str(e)}")

            except StopIteration:
                break


migrate_vertex = MigrateUser()
migrate_vertex.migrateUser()
