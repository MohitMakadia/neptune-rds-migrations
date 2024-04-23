# type: ignore[import]
from models.Verification import Verification, Base
from utils.connect import rdsConnect, neptuneConnect
from gremlin_python.structure.graph import Graph
from utils.session import createRdsSession, commitRds
from utils.validation import validate_uuid, checkIfTableExists
 
class MigrateVerification:
    
    def __init__(self):
        self.engine = rdsConnect()
        self.neptune_engine = neptuneConnect()
        self.g = Graph().traversal().withRemote(self.neptune_engine)
        self.table = "Verification"
              
    def createVerificationTable(self):
        print(f'Creating {self.table} Table ...')
        Verification.tableLaunch()
        print(f'{self.table} Table Created')

    def migrateVerification(self):
        checkIfTableExists(self.engine, self.table)
        self.createVerificationTable()
        print(f'Starting Migration for {self.table} table ...')
        
        with createRdsSession() as session:
            vertexIds = self.g.V().hasLabel("verification").toList()
            for vertexId in vertexIds:
                workers_to_add = []
                verificationValueMaps = self.g.V(vertexId).valueMap().toList()
                try:                        
                    for verificationValueMap in verificationValueMaps:
                        outVertexs = self.g.V(vertexId.id).out().toList()
                        for outVertex in outVertexs:
                            verification = Verification(
                                last_login = verificationValueMap.get("last_login", [None])[0],
                                type = verificationValueMap.get("type", [None])[0],
                                used_to_verify = outVertex.id,
                                verification_id = vertexId.id
                            )
                            workers_to_add.append(verification)
                        session.add_all(workers_to_add)
                except Exception as e:
                    print(f"Error migrating verification with ID {vertexId}: {str(e)}")
            session.commit()        
                
migrate_verification = MigrateVerification()
migrate_verification.migrateVerification()
