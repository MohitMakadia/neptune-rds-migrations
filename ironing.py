# type: ignore[import]
from models.Ironing import Ironing, Base
from utils.connect import rdsConnect, neptuneConnect
from gremlin_python.structure.graph import Graph
from utils.session import createRdsSession, commitRds
from utils.validation import validate_uuid, checkIfTableExists
 
class MigrateIroning:
    def __init__(self):
        self.engine = rdsConnect()
        self.neptune_engine = neptuneConnect()
        self.g = Graph().traversal().withRemote(self.neptune_engine)
        self.table = "Ironing"

    def createmigrateIroningTable(self):
        print(f'Creating {self.table} Table ...')
        Ironing.tableLaunch()
        print(f'{self.table} Table Created')

    def migrateIroning(self):
        checkIfTableExists(self.engine, self.table)
        self.createmigrateIroningTable()
        print(f'Starting Migration for {self.table} table ...')

        vertexIds = [v.id for v in self.g.V().hasLabel("ironing").toList()]
        vertexIterate = iter(vertexIds)

        while True:
            try:
                vertexId = next(vertexIterate)
                # if validate_uuid(vertexId):
                  
                blocks_vertices = self.g.V(vertexId).out("blocks").toList()
                blocks_ids = [vertex.id for vertex in blocks_vertices]


                handling_required_by_vertices = self.g.V(vertexId).out("handling_required_by").toList()
                handling_required_by_ids = [vertex.id for vertex in handling_required_by_vertices]

                try:
                    session = createRdsSession()

                    for blocks_id in blocks_ids:
                        
                        ironing = Ironing(
                            ironing_id=vertexId,
                            blocks=blocks_id,
                            handling_required_by=None,
                        )
                        session.add(ironing)

                    for handling_required_by_id in handling_required_by_ids:
                        
                        ironing = Ironing(
                            ironing_id=vertexId,
                            blocks=None,
                            handling_required_by=handling_required_by_id,
                        )
                        session.add(ironing)
                            
                    commitRds(session)
                    
                except Exception as e:
                    print(f'Failed due to {str(e)}')
                # else:
                #     print(f'Invalid UUID Detected {vertexId} ... Skipping.')
            except StopIteration:
                break

migrate_review = MigrateIroning()
migrate_review.migrateIroning()