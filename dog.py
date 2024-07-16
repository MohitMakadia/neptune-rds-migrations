# type: ignore[import]
from models.Dog import Dog
from utils.connect import rds_connect, neptune_connect
from gremlin_python.structure.graph import Graph
from utils.session import create_rds_session, commit_rds
from utils.validation import check_if_table_exists


class MigrateDog:
    def __init__(self):
        self.engine = rds_connect()
        self.neptune_engine = neptune_connect()
        self.g = Graph().traversal().withRemote(self.neptune_engine)
        self.table = "Dog"

    def create_migrate_dog_table(self):
        print(f"Creating {self.table} Table ...")
        Dog.table_launch()
        print(f"{self.table} Table Created")

    def migrate_dog(self):
        check_if_table_exists(self.engine, self.table)
        self.create_migrate_dog_table()
        print(f"Starting Migration for {self.table} table ...")
        session = create_rds_session()
        vertex_ids = [v.id for v in self.g.V().hasLabel("dog").toList()]
        for vertex_id in vertex_ids:
            dogs_to_add = []
            blocks_vertices = self.g.V(vertex_id).out("blocks").toList()
            blocks_ids = [vertex.id for vertex in blocks_vertices]
            handling_required_by_vertices = (
                self.g.V(vertex_id).out("handling_required_by").toList()
            )
            handling_required_by_ids = [
                vertex.id for vertex in handling_required_by_vertices
            ]
            try:
                for blocks_id in blocks_ids:
                    dog_blocks = Dog(
                        dog_id=vertex_id,
                        blocks=blocks_id,
                        handling_required_by=None,
                    )
                    dogs_to_add.append(dog_blocks)

                for handling_required_by_id in handling_required_by_ids:
                    dog_handling_required_by = Dog(
                        dog_id=vertex_id,
                        blocks=None,
                        handling_required_by=handling_required_by_id,
                    )
                    dogs_to_add.append(dog_handling_required_by)
            except Exception as e:
                print(f"Failed due to {str(e)}")
            session.add_all(dogs_to_add)
        session.commit()


migrate_review = MigrateDog()
migrate_review.migrate_dog()
