# type: ignore[import]
from models.Worker import Worker, Base
from utils.connect import rdsConnect, neptuneConnect
from gremlin_python.structure.graph import Graph
from sqlalchemy import inspect
from utils.session import createRdsSession, commitRds
from utils.validation import validate_uuid, checkIfTableExists

class migrateWorker:
    
    def __init__(self):
        self.engine = rdsConnect()
        self.neptune_engine = neptuneConnect()
        self.g = Graph().traversal().withRemote(self.neptune_engine)
        self.table = "Worker"
              
    def createWorkerTable(self):
        print(f'Creating {self.table} Table ...')
        Worker.tableLaunch()
        print(f'{self.table} Table Created')

    def migrateWorker(self):
        checkIfTableExists(self.engine, self.table)
        self.createWorkerTable()
        print(f'Starting Migration for {self.table} table ...')
        with createRdsSession() as session:
            vertexIds = self.g.V().hasLabel("worker").toList()
            for vertexId in vertexIds:
                if validate_uuid(vertexId.id):
                    workerValueMaps = self.g.V(vertexId).valueMap().toList()
                    for workerValueMap in workerValueMaps:
                        Base.metadata.bind = self.engine
                        session = createRdsSession()
                        try:
                            worker = Worker(
                                id = vertexId.id,
                                amount = workerValueMap.get("amount", [None])[0],
                                domain_language = workerValueMap.get("domain_language", [None])[0],
                                domain = workerValueMap.get("domain", [None])[0],
                                email = workerValueMap.get("email", [None])[0],
                                experience = workerValueMap.get("experience", [None])[0],
                                first_name = workerValueMap.get("first_name", [None])[0],
                                internal_score = workerValueMap.get("internal_score", [None])[0],
                                is_online = workerValueMap.get("is_online", [None])[0],
                                is_suspended = workerValueMap.get("is_suspended", [None])[0],
                                last_login = workerValueMap.get("last_login", [None])[0],
                                location_address = workerValueMap.get("location_address", [None])[0],
                                location_city = workerValueMap.get("location_city", [None])[0],
                                location_country = workerValueMap.get("location_country", [None])[0],
                                location_longitude = workerValueMap.get("location_longitude", [None])[0],
                                location_latitude = workerValueMap.get("location_latitude", [None])[0],
                                location_place_id = workerValueMap.get("location_place_id", [None])[0],
                                location_slug = workerValueMap.get("location_slug", [None])[0],
                                max_distance = workerValueMap.get("max_distance", [None])[0],
                                personal_note = workerValueMap.get("personal_note", [None])[0],
                                profile_picture = workerValueMap.get("profile_picture", [None])[0],
                                published = workerValueMap.get("published", [False])[None],
                                registered_date = workerValueMap.get("registered_date", [None])[0],
                                score = workerValueMap.get("score", [0])[None],
                                user_alert = workerValueMap.get("user_alert", [None])[0],
                                votes = workerValueMap.get("votes", [None])[0],
                                )
                            session.add(worker)
                            commitRds(session)
                        except Exception as e:
                            print(str(e))
                            session.close()

                else:
                    print(f'Invalid UUID Detected {vertexId.id} ... Skipping.')

worker = migrateWorker()
worker.migrateWorker()