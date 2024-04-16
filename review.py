# type: ignore[import]
from models.Review import Review, Base
from utils.connect import rdsConnect, neptuneConnect
from gremlin_python.structure.graph import Graph
from utils.session import createRdsSession, commitRds
from utils.validation import validate_uuid, checkIfTableExists
 
class MigrateReview:
    def __init__(self):
        self.engine = rdsConnect()
        self.neptune_engine = neptuneConnect()
        self.g = Graph().traversal().withRemote(self.neptune_engine)
        self.table = "Review"

    def createReviewTable(self):
        print(f'Creating {self.table} Table ...')
        Review.tableLaunch()
        print(f'{self.table} Table Created')

    def migrateReview(self):
        checkIfTableExists(self.engine, self.table)
        self.createReviewTable()
        print(f'Starting Migration for {self.table} table ...')

        vertexIds = [v.id for v in self.g.V().hasLabel("review").toList()]
        vertexIterate = iter(vertexIds)

        while True:
            try:
                vertexId = next(vertexIterate)
                if validate_uuid(vertexId):
                    Base.metadata.bind = self.engine
                    reviewValueMap = self.g.V(vertexId).valueMap().toList()[0]

                    # Query for evaluated vertex
                    evaluated_vertex = self.g.V(vertexId).out("evaluated").next()
                    evaluated_id = evaluated_vertex.id if evaluated_vertex is not None else None

                    # Query for written_by vertex
                    written_by_vertex = self.g.V(vertexId).out("written_by").next()
                    written_by_id = written_by_vertex.id if written_by_vertex is not None else None

                    try:
                        session = createRdsSession()
                        review = Review(
                            review_id=vertexId,
                            score=reviewValueMap.get("score", [0])[0],
                            text=reviewValueMap.get("text", [""])[0],
                            evaluated=evaluated_id,
                            written_by=written_by_id,
                        )

                        session.add(review)
                        commitRds(session)
                        
                    except Exception as e:
                        print(f'Failed due to {str(e)}')
                else:
                    print(f'Invalid UUID Detected {vertexId} ... Skipping.')
            except StopIteration:
                break

migrate_review = MigrateReview()
migrate_review.migrateReview()