# type: ignore[import]
from models.Dog import Dog , Base
from utils.connect import rdsConnect, neptuneConnect
from gremlin_python.structure.graph import Graph
from utils.session import createRdsSession, commitRds
from utils.validation import validate_uuid, checkIfTableExists
 
class MigrateDog:
    def __init__(self):
        self.engine = rdsConnect()
        self.neptune_engine = neptuneConnect()
        self.g = Graph().traversal().withRemote(self.neptune_engine)
        self.table = "Dog"

    def createmigrateDogTable(self):
        print(f'Creating {self.table} Table ...')
        Dog.tableLaunch()
        print(f'{self.table} Table Created')

    def migrateDog(self):
        checkIfTableExists(self.engine, self.table)
        self.createmigrateDogTable()
        print(f'Starting Migration for {self.table} table ...')

        vertexIds = [v.id for v in self.g.V().hasLabel("dog").toList()]
        vertexIterate = iter(vertexIds)

        while True:
            try:
                vertexId = next(vertexIterate)
                # if validate_uuid(vertexId) and validate_uuid(vertexId) and validate_uuid(vertexId):
                 
                blocks_vertices = self.g.V(vertexId).out("blocks").toList()
                blocks_ids = [vertex.id for vertex in blocks_vertices]


                handling_required_by_vertices = self.g.V(vertexId).out("handling_required_by").toList()
                handling_required_by_ids = [vertex.id for vertex in handling_required_by_vertices]

                try:
                    session = createRdsSession()
                    for blocks_id in blocks_ids:
                        # if validate_uuid(blocks_id):
                        dog = Dog(
                            dog_id=vertexId,
                            blocks=blocks_id,
                            handling_required_by=None,
                        )
                        session.add(dog)
                        # else:
                        #     print(f'Invalid UUID Detected {blocks_id} ... Skipping.')

                    for handling_required_by_id in handling_required_by_ids:
                        # if validate_uuid(handling_required_by_id):                            
                        dog = Dog(
                            dog_id=vertexId,
                            blocks=None,
                            handling_required_by=handling_required_by_id,
                        )
                        session.add(dog)
                        # else:
                        #     print(f'Invalid UUID Detected {handling_required_by_id} ... Skipping.')       
                    commitRds(session)
                    
                except Exception as e:
                    print(f'Failed due to {str(e)}')
                # else:
                #     print(f'Invalid UUID Detected {vertexId} ... Skipping.')
            except StopIteration:
                break

migrate_review = MigrateDog()
migrate_review.migrateDog()