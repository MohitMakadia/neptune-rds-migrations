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
                                amount = workerValueMap.get("amount", [0])[0],
                                domain_language = workerValueMap.get("domain_language", [""])[0],
                                domain = workerValueMap.get("domain", [""])[0],
                                email = workerValueMap.get("email", [""])[0],
                                experience = workerValueMap.get("experience", [0])[0],
                                first_name = workerValueMap.get("first_name", [""])[0],
                                internal_score = workerValueMap.get("internal_score", [0])[0],
                                is_online = workerValueMap.get("is_online", [False])[0],
                                is_suspended = workerValueMap.get("is_suspended", [False])[0],
                                last_login = workerValueMap.get("last_login", [0])[0],
                                location_address = workerValueMap.get("location_address", [""])[0],
                                location_city = workerValueMap.get("location_city", [""])[0],
                                location_country = workerValueMap.get("location_country", [""])[0],
                                location_longitude = workerValueMap.get("location_longitude", [0.0])[0],
                                location_latitude = workerValueMap.get("location_latitude", [0.0])[0],
                                location_place_id = workerValueMap.get("location_place_id", [""])[0],
                                location_slug = workerValueMap.get("location_slug", [""])[0],
                                max_distance = workerValueMap.get("max_distance", [0])[0],
                                personal_note = workerValueMap.get("personal_note", [""])[0],
                                profile_picture = workerValueMap.get("profile_picture", [""])[0],
                                published = workerValueMap.get("published", [False])[0],
                                registered_date = workerValueMap.get("registered_date", [0])[0],
                                score = workerValueMap.get("score", [0])[0],
                                user_alert = workerValueMap.get("user_alert", [False])[0],
                                votes = workerValueMap.get("votes", [0])[0],
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