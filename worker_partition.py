# type: ignore[import]
from models.Worker import Worker, Base
from utils.connect import rdsConnect, neptuneConnect
from gremlin_python.structure.graph import Graph
from sqlalchemy import inspect
from utils.session import createRdsSession, commitRds
from utils.validation import validate_uuid, checkIfTableExists
import ast
import os

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

    def processChunks(self):
        input_file = "worker.txt"
        with open("chunks/" + input_file, "r") as f:
            chunks_str = f.read()

        chunks = ast.literal_eval(chunks_str)
        return chunks.items()
    
    def markChunkCompleted(self, chunk_num, status):

        chunks_folder = "chunks/worker_status"
        if not os.path.exists(chunks_folder):
            os.makedirs(chunks_folder)
        
        completed_file = f"chunks/worker_status/completed_{chunk_num}.txt"
        
        with open(completed_file, "w") as f:
            f.write(str({chunk_num: [status]}))

    def migrateWorker(self):
        checkIfTableExists(self.engine, self.table)
        self.createWorkerTable()
        print(f'Starting Migration for {self.table} table ...')
        Base.metadata.bind = self.engine
        chunks = self.processChunks()
        for chunk_name, chunk_data in chunks:
            for vertexId in chunk_data:
                workerValueMap = self.g.V(vertexId).valueMap().toList()[0]
                outEdges = self.g.V(vertexId).outE().toList()
                for edge in outEdges:
                    session = createRdsSession()
                    try:
                        outVertexId = str(edge).split("][")[1].split("->")[1][:-1]
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
                            speaks = None
                            verified_by = None
                            wants_payment_in = None
                            works_on = None
                            participates_in = None
                            receives = None
                            favored_by = None
                            authored = None
                            wrote = None
                            is_evaluated_by = None
                            blocked_by = None
                            issued = None
                            favors = None
                            wants_to_pay_in = None
                            wants_service_on = None
                            )
                        
                        if edge.label == "speaks":
                            customer.speaks = outVertexId

                        if edge.label == "verified_by":
                            customer.verified_by = outVertexId

                        if edge.label == "wants_payment_in":
                            customer.wants_payment_in = outVertexId

                        if edge.label == "works_on":
                            customer.works_on = outVertexId

                        if edge.label == "participates_in":
                            customer.participates_in = outVertexId

                        if edge.label == "receives":
                            customer.receives = outVertexId

                        if edge.label == "favored_by":
                            customer.favored_by = outVertexId
                            
                        if edge.label == "authored":
                            customer.authored = outVertexId

                        if edge.label == "wrote":
                            customer.wrote = outVertexId

                        if edge.label == "is_evaluated_by":
                            customer.is_evaluated_by = outVertexId

                        if edge.label == "blocked_by":
                            customer.is_evaluated_by = outVertexId

                        if edge.label == "issued":
                            customer.issued = outVertexId

                        if edge.label == "favors":
                            customer.favors = outVertexId

                        if edge.label == "wants_to_pay_in":
                            customer.wants_to_pay_in = outVertexId
                        
                        if edge.label == "wants_service_on":
                            customer.wants_service_on = outVertexId

                        session.add(worker)
                        commitRds(session)

                    except Exception as e:
                        print(str(e))
                        session.close()

            self.markChunkCompleted(chunk_name, "Completed")
                   

worker = migrateWorker()
worker.migrateWorker()