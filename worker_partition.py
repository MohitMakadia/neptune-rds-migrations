# type: ignore[import]
from models.Worker import Worker, Base
from utils.connect import rdsConnect, neptuneConnect
from gremlin_python.structure.graph import Graph
from utils.session import createRdsSession
from utils.validation import checkIfTableExists
import ast
import os
import sys


class migrateWorker:

    def __init__(self, chunk_number):
        self.engine = rdsConnect()
        self.neptune_engine = neptuneConnect()
        self.g = Graph().traversal().withRemote(self.neptune_engine)
        self.table = "NewWorker"
        self.chunk_number = chunk_number

    def createWorkerTable(self):
        print(f'Creating {self.table} Table ...')
        Worker.tableLaunch()
        print(f'{self.table} Table Created')

    def processChunks(self, key):
        input_file = "worker.txt"
        with open("chunks/" + input_file, "r") as f:
            chunks_str = f.read()

        chunks = ast.literal_eval(chunks_str)
        for k, v in chunks.items():
            if k == key:
                return k, v

        return None, None

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
        chunk_name, chunk_data = self.processChunks(self.chunk_number)
        print("Chunk -> ", chunk_name)
        session = createRdsSession()
        try:
            for vertexId in chunk_data:
                workers_to_add = []
                workerValueMap = self.g.V(vertexId).valueMap().toList()[0]
                outEdges = self.g.V(vertexId).outE().toList()
                for edge in outEdges:

                    try:
                        outVertexId = str(edge).split(
                            "][")[1].split("->")[1][:-1]
                        worker = Worker(
                            worker_id=vertexId,
                            amount=workerValueMap.get("amount", [None])[0],
                            domain_language=workerValueMap.get(
                                "domain_language", [None])[0],
                            domain=workerValueMap.get("domain", [None])[0],
                            email=workerValueMap.get("email", [None])[0],
                            experience=workerValueMap.get(
                                "experience", [None])[0],
                            first_name=workerValueMap.get(
                                "first_name", [None])[0],
                            internal_score=workerValueMap.get(
                                "internal_score", [None])[0],
                            is_online=workerValueMap.get(
                                "is_online", [False])[0],
                            is_suspended=workerValueMap.get(
                                "is_suspended", [False])[0],
                            is_deleted=workerValueMap.get(
                                "is_deleted", [False])[0],
                            last_login=workerValueMap.get(
                                "last_login", [None])[0],
                            location_address=workerValueMap.get(
                                "location_address", [None])[0],
                            location_city=workerValueMap.get(
                                "location_city", [None])[0],
                            location_country=workerValueMap.get(
                                "location_country", [None])[0],
                            location_longitude=workerValueMap.get(
                                "location_longitude", [None])[0],
                            location_latitude=workerValueMap.get(
                                "location_latitude", [None])[0],
                            location_place_id=workerValueMap.get(
                                "location_place_id", [None])[0],
                            location_slug=workerValueMap.get(
                                "location_slug", [None])[0],
                            max_distance=workerValueMap.get(
                                "max_distance", [None])[0],
                            personal_note=workerValueMap.get(
                                "personal_note", [None])[0],
                            profile_picture=workerValueMap.get(
                                "profile_picture", [None])[0],
                            published=workerValueMap.get(
                                "published", [False])[0],
                            registered_date=workerValueMap.get(
                                "registered_date", [None])[0],
                            score=workerValueMap.get("score", [None])[0],
                            user_alert=workerValueMap.get(
                                "user_alert", [False])[0],
                            votes=workerValueMap.get("votes", [None])[0],
                            speaks=None,
                            verified_by=None,
                            wants_payment_in=None,
                            works_on=None,
                            participates_in=None,
                            receives=None,
                            favored_by=None,
                            authored=None,
                            wrote=None,
                            is_evaluated_by=None,
                            blocked_by=None,
                            issued=None,
                            favors=None,
                            wants_to_pay_in=None,
                            wants_service_on=None
                        )

                        if edge.label == "speaks":
                            worker.speaks = outVertexId

                        if edge.label == "verified_by":
                            worker.verified_by = outVertexId

                        if edge.label == "wants_payment_in":
                            worker.wants_payment_in = outVertexId

                        if edge.label == "works_on":
                            worker.works_on = outVertexId

                        if edge.label == "participates_in":
                            worker.participates_in = outVertexId

                        if edge.label == "receives":
                            worker.receives = outVertexId

                        if edge.label == "favored_by":
                            worker.favored_by = outVertexId

                        if edge.label == "authored":
                            worker.authored = outVertexId

                        if edge.label == "wrote":
                            worker.wrote = outVertexId

                        if edge.label == "is_evaluated_by":
                            worker.is_evaluated_by = outVertexId

                        if edge.label == "blocked_by":
                            worker.is_evaluated_by = outVertexId

                        if edge.label == "issued":
                            worker.issued = outVertexId

                        if edge.label == "favors":
                            worker.favors = outVertexId

                        if edge.label == "wants_to_pay_in":
                            worker.wants_to_pay_in = outVertexId

                        if edge.label == "wants_service_on":
                            worker.wants_service_on = outVertexId

                        workers_to_add.append(worker)

                    except Exception as e:
                        print(str(e))

                session.add_all(workers_to_add)
            session.commit()

        except Exception as e:
            print(str(e))
            session.rollback()

        finally:
            session.close()

        self.markChunkCompleted(chunk_name, "Completed")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 worker_partition.py <chunk_number>")
        sys.exit(1)

    chunk_number = int(sys.argv[1])
    worker = migrateWorker(chunk_number)
    worker.migrateWorker()
