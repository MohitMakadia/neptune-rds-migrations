# type: ignore[import]
from models.Verification_Code import VerificationCode, Base
from utils.connect import rdsConnect, neptuneConnect
from gremlin_python.structure.graph import Graph
from utils.session import createRdsSession, commitRds
from utils.validation import checkIfTableExists

class MigrateVerificationCode:
    
    def __init__(self):
        self.engine = rdsConnect()
        self.neptune_engine = neptuneConnect()
        self.g = Graph().traversal().withRemote(self.neptune_engine)
        self.table = "VerificationCode"
    
    def createVerificationCodeTable(self):
        print(f'Creating {self.table} Table ...')
        VerificationCode.tableLaunch()
        print(f'{self.table} Table Created')
              
    def migrateVerificationCode(self):
        checkIfTableExists(self.engine, self.table)
        self.createVerificationCodeTable()
        print(f'Starting Migration for {self.table} table ...')

        vertexIds = [v.id for v in self.g.V().hasLabel("verification_code").toList()]
        vertexIterate = iter(vertexIds)

        while True: 
            try:
                vertexId = next(vertexIterate)
                Base.metadata.bind = self.engine
                verificationCodeValueMap = self.g.V(vertexId).valueMap().toList()[0]

                try:
                    session = createRdsSession()
                    verificationcode = VerificationCode(
                        verificationcode_id=vertexId,
                        active= verificationCodeValueMap.get("is_online", [None])[0],
                        created_timestamp= verificationCodeValueMap.get("created_timestamp", [None])[0],
                        person_id=verificationCodeValueMap.get("person_id", [None])[0],
                        
                    )

                    session.add(verificationcode)
                    commitRds(session)
                    
                except Exception as e:
                    print(f'Failed due to {str(e)}')
                
            except StopIteration:
                break

migrate_review = MigrateVerificationCode()
migrate_review.migrateVerificationCode()