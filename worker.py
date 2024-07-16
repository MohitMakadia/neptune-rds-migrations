# type: ignore[import]
from models.Worker import Worker, Base
from utils.connect import rds_connect, neptune_connect
from gremlin_python.structure.graph import Graph
from utils.session import create_rds_session, commit_rds
from utils.validation import check_if_table_exists


class migrateWorker:

    def __init__(self):
        self.engine = rds_connect()
        self.neptune_engine = neptune_connect()
        self.g = Graph().traversal().withRemote(self.neptune_engine)
        self.table = "Worker"

    def createWorkerTable(self):
        print(f"Creating {self.table} Table ...")
        Worker.table_launch()
        print(f"{self.table} Table Created")

    def migrateWorker(self):
        check_if_table_exists(self.engine, self.table)
        self.createWorkerTable()
        print(f"Starting Migration for {self.table} table ...")
        Base.metadata.bind = self.engine
        vertexIds = self.g.V().hasLabel("worker").toList()
        for vertexId in vertexIds:
            workerValueMap = self.g.V(vertexId).valueMap().toList()[0]
            outEdges = self.g.V(vertexId).outE().toList()
            for edge in outEdges:
                session = create_rds_session()
                try:
                    outVertexId = str(edge).split("][")[1].split("->")[1][:-1]
                    worker = Worker(
                        worker_id=vertexId.id,
                        amount=workerValueMap.get("amount", [None])[0],
                        domain_language=workerValueMap.get("domain_language", [None])[
                            0
                        ],
                        domain=workerValueMap.get("domain", [None])[0],
                        email=workerValueMap.get("email", [None])[0],
                        experience=workerValueMap.get("experience", [None])[0],
                        first_name=workerValueMap.get("first_name", [None])[0],
                        internal_score=workerValueMap.get("internal_score", [None])[0],
                        is_online=workerValueMap.get("is_online", [None])[0],
                        is_suspended=workerValueMap.get("is_suspended", [None])[0],
                        last_login=workerValueMap.get("last_login", [None])[0],
                        location_address=workerValueMap.get("location_address", [None])[
                            0
                        ],
                        location_city=workerValueMap.get("location_city", [None])[0],
                        location_country=workerValueMap.get("location_country", [None])[
                            0
                        ],
                        location_longitude=workerValueMap.get(
                            "location_longitude", [None]
                        )[0],
                        location_latitude=workerValueMap.get(
                            "location_latitude", [None]
                        )[0],
                        location_place_id=workerValueMap.get(
                            "location_place_id", [None]
                        )[0],
                        location_slug=workerValueMap.get("location_slug", [None])[0],
                        max_distance=workerValueMap.get("max_distance", [None])[0],
                        personal_note=workerValueMap.get("personal_note", [None])[0],
                        profile_picture=workerValueMap.get("profile_picture", [None])[
                            0
                        ],
                        published=workerValueMap.get("published", [None])[0],
                        registered_date=workerValueMap.get("registered_date", [None])[
                            0
                        ],
                        score=workerValueMap.get("score", [None])[0],
                        user_alert=workerValueMap.get("user_alert", [None])[0],
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
                        wants_service_on=None,
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

                    session.add(worker)
                    commit_rds(session)

                except Exception as e:
                    print(str(e))
                    session.close()


worker = migrateWorker()
worker.migrateWorker()
