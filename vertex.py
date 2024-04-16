# type: ignore[import]
from models.Vertex import Vertex, Base
from utils.connect import rdsConnect, neptuneConnect
from gremlin_python.structure.graph import Graph
from utils.session import createRdsSession, commitRds
from utils.validation import validate_uuid, checkIfTableExists
 
class MigrateVertex:
    def __init__(self):
        self.engine = rdsConnect()
        self.neptune_engine = neptuneConnect()
        self.g = Graph().traversal().withRemote(self.neptune_engine)
        self.table = "Vertex"

    def createVertexTable(self):
        print(f'Creating {self.table} Table ...')
        Vertex.tableLaunch()
        print(f'{self.table} Table Created')


    def migrateVertex(self):
        checkIfTableExists(self.engine, self.table)
        self.createVertexTable()
        print(f'Starting Migration for {self.table} table ...')

        vertexIds = [v.id for v in self.g.V().hasLabel("vertex").toList()]
        vertexIterate = iter(vertexIds)

        while True:
            try:
                vertexId = next(vertexIterate)
                if validate_uuid(vertexId):
                    Base.metadata.bind = self.engine
                    vertexValueMap = self.g.V(vertexId).valueMap().toList()[0]

                    try:
                        session = createRdsSession()
                        vertex = Vertex(
                            vertex_id=vertexId,
                            last_login = vertexValueMap.get("last_login", [0])[0],
                        )
                        session.add(vertex)
                        commitRds(session)
                    except Exception as e:
                        print(f'Failed due to {str(e)}')
                else:
                    print(f'Invalid UUID Detected {vertexId} ... Skipping.')
            except StopIteration:
                break

migrate_vertex= MigrateVertex()
migrate_vertex.migrateVertex()