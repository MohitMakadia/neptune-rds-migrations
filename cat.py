# type: ignore[import]
from models.Cat import Cat
from utils.connect import rds_connect, neptune_connect
from gremlin_python.structure.graph import Graph
from utils.session import create_rds_session, commit_rds
from utils.validation import check_if_table_exists


class MigrateCat:
    def __init__(self):
        self.engine = rds_connect()
        self.neptune_engine = neptune_connect()
        self.g = Graph().traversal().withRemote(self.neptune_engine)
        self.table = "Cat"

    def create_migrate_cat_table(self):
        print(f"Creating {self.table} Table ...")
        Cat.table_launch()
        print(f"{self.table} Table Created")

    def migrate_cat(self):
        check_if_table_exists(self.engine, self.table)
        self.create_migrate_cat_table()
        print(f"Starting Migration for {self.table} table ...")
        session = create_rds_session()
        vertex_ids = [v.id for v in self.g.V().hasLabel("cat").toList()]
        for vertex_id in vertex_ids:
            cats_to_add = []
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
                    cat = Cat(
                        cat_id=vertex_id,
                        blocks=blocks_id,
                        handling_required_by=None,
                    )
                    cats_to_add.append(cat)
                for handling_required_by_id in handling_required_by_ids:
                    cat = Cat(
                        cat_id=vertex_id,
                        blocks=None,
                        handling_required_by=handling_required_by_id,
                    )
                    cats_to_add.append(cat)
            except Exception as e:
                print(f"Failed due to {str(e)}")
            session.add_all(cats_to_add)
        session.commit()


migrate_review = MigrateCat()
migrate_review.migrate_cat()
