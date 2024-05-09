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
        session = createRdsSession()
        try:
            for vertexId in vertexIds:
                review_to_add = []
                Base.metadata.bind = self.engine
                reviewValueMap = self.g.V(vertexId).valueMap().toList()[0]
                outEdges = self.g.V(vertexId).outE().toList()
                
                author_id = None
                receiver_id = None
                customer_id = None
                worker_id = None

                for edge in outEdges:
                    outVertexId = str(edge).split("][")[1].split("->")[1][:-1]
                    
                    if edge.label == "written_by":
                        author_id = outVertexId

                    if edge.label == "evaluated":
                        receiver_id = outVertexId

                    if self.g.V(outVertexId).label().next() == "customer":
                        customer_id = outVertexId

                    elif self.g.V(outVertexId).label().next() == "worker":
                        worker_id = outVertexId
                try:
                    review = Review(
                        review_id=vertexId,
                        score=reviewValueMap.get("score", [None])[0],
                        text=reviewValueMap.get("text", [None])[0],
                        author_id=author_id,
                        receiver_id=receiver_id,
                        customer_id=customer_id,
                        worker_id=worker_id
                    )
                    
                    review_to_add.append(review)
            
                except Exception as e:
                    print(f'Failed due to {str(e)}')

                session.add_all(review_to_add)
            session.commit()
        
        except Exception as e:
            print(str(e))
            session.rollback()
        
        finally:
            session.close()

migrate_review = MigrateReview()
migrate_review.migrateReview()