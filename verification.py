# type: ignore[import]
from models.Verification import Verification, Base  # Import Verification and Base classes
from utils.connect import rdsConnect, neptuneConnect
from gremlin_python.structure.graph import Graph
from sqlalchemy import inspect
from utils.rdsSession import createRdsSession, commitRds
import uuid
from sqlalchemy.orm import relationship
 
class MigrateVerification:
    
    def __init__(self):
        self.engine = rdsConnect()
        self.neptune_engine = neptuneConnect()
        self.g = Graph().traversal().withRemote(self.neptune_engine)
        self.table = "Verification"  # Correct table name to "Verification"
              
    def checkIfTableExists(self):
        inspector = inspect(self.engine)
        if self.table in inspector.get_table_names():
            print(f'Table {self.table} exists.')
        else:
            print(f'Table {self.table} does not exist.')

    def createVerificationTable(self):  # Correct method name
        print(f'Creating {self.table} Table ...')
        Verification.tableLaunch()  # Call Verification.tableLaunch() to create the table
        print(f'{self.table} Table Created')

    def validate_uuid(self, uuid_str):
        try:
            # Extract the UUID string representation from the Vertex object
            uuid_string = str(uuid_str)
            uuid.UUID(uuid_string)
            return True
        except (ValueError, AttributeError):
            return True


    def migrateVerification(self):
        self.checkIfTableExists()
        self.createVerificationTable()  # No need to call this, as Verification.tableLaunch() is called inside the loop
        print(f'Starting Migration for {self.table} table ...')
        
        with createRdsSession() as session:
            vertexIds = self.g.V().hasLabel("verification").toList()
            print(vertexIds)
            for vertexId in vertexIds:
                if self.validate_uuid(vertexId):
                    verificationValueMaps = self.g.V(vertexId).valueMap().toList()
                    print(verificationValueMaps)
                    try:
                        for verificationValueMap in verificationValueMaps:
                            outVertexs = self.g.V(verificationValueMap).out().id()
                            print(outVertexs)
                            # for outVertex in outVertexs: 
                            #     verification = Verification(
                            #         used_to_verify_id=vertexId,
                            #         last_login=verificationValueMap.get("last_login", 0),
                            #         type_email=verificationValueMap.get("type_email", ""),
                            #         user_id=outVertex.id,
                            #         #worker_id=verificationValueMap.get("worker_id", ""),
                            #         #worker=#relationship("Worker", back_populates="verifications"),
                            #         #customer=#relationship("Customer", back_populates="verifications"),
                            #     )
                            #     session.add(verification)
                            #     commitRds(session)
                    except Exception as e:
                        print(f"Error migrating verification with ID {vertexId}: {str(e)}")
                else:
                    print(f'Invalid UUID Detected {vertexId} ... Skipping.')

# Usage:
migrate_verification = MigrateVerification()
migrate_verification.migrateVerification()
