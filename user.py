# type: ignore[import]
from models.User import User, Base
from utils.connect import rdsConnect, neptuneConnect
from gremlin_python.structure.graph import Graph
from utils.session import createRdsSession, commitRds
from utils.validation import checkIfTableExists
 
class MigrateUser:
    def __init__(self):
        self.engine = rdsConnect()
        self.neptune_engine = neptuneConnect()
        self.g = Graph().traversal().withRemote(self.neptune_engine)
        self.table = "User"

    def createUserTable(self):
        print(f'Creating {self.table} Table ...')
        User.tableLaunch()
        print(f'{self.table} Table Created')


    def migrateUser(self):
        checkIfTableExists(self.engine, self.table)
        self.createUserTable()
        print(f'Starting Migration for {self.table} table ...')

        vertexIds = [v.id for v in self.g.V().hasLabel("user").toList()]
        vertexIterate = iter(vertexIds)

        while True:
            try:
                vertexId = next(vertexIterate)
                
                Base.metadata.bind = self.engine
                
                favors_vertex = self.g.V(vertexId).out("favors").next()  
                favors_id = favors_vertex.id if favors_vertex is not None else None

                try:
                    session = createRdsSession()
                    user = User(
                        user_id=vertexId,
                        favors=favors_id,
                    )
                    session.add(user)
                    commitRds(session)
                
                except Exception as e:
                    print(f'Failed due to {str(e)}')
                
            except StopIteration:
                break

migrate_vertex = MigrateUser()
migrate_vertex.migrateUser()
