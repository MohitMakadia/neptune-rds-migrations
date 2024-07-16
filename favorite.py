# type: ignore[import]
from models.Favourite import Favourite, Base
from utils.connect import rds_connect, neptune_connect
from gremlin_python.structure.graph import Graph
from utils.session import create_rds_session
from utils.validation import check_if_table_exists
import sys
import ast
import os


class migrateFavorite:
    def __init__(self, file_name, chunk_number):
        self.engine = rds_connect()
        self.neptune_engine = neptune_connect()
        self.g = Graph().traversal().withRemote(self.neptune_engine)
        self.table = "Favourite"
        self.chunk_number = chunk_number
        self.file_name = file_name

    def create_favorite_table(self):
        print(f"Creating {self.table} Table ...")
        Favourite.table_launch()
        print(f"{self.table} Table Created")

    def process_chunks(self, key):
        input_file = self.file_name
        with open("chunks/" + input_file, "r") as f:
            chunks_str = f.read()

        chunks = ast.literal_eval(chunks_str)
        for k, v in chunks.items():
            if k == key:
                return k, v

        return None, None

    def migrate_favorite(self):
        check_if_table_exists(self.engine, self.table)
        self.create_favorite_table()
        print(f"Starting Migration for {self.table} table ...")
        Base.metadata.bind = self.engine
        # vertexIds = self.g.V().hasLabel("customer").toList()
        chunk_name, chunk_data = self.process_chunks(self.chunk_number)
        session = create_rds_session()
        for vertexId in chunk_data:
            out_edges = self.g.V(vertexId).outE().toList()
            favored_by = None
            favors = None
            for edge in out_edges:
                out_vertex_id = str(edge).split("][")[1].split("->")[1][:-1]

                if edge.label == "favored_by":
                    favored_by = out_vertex_id

                if edge.label == "favors":
                    favors = out_vertex_id

                if favored_by is not None or favors is not None:
                    if edge.label == "favored_by" or edge.label == "favors":
                        try:
                            favorite = Favourite(
                                person_id=vertexId, favored_by=favored_by, favors=favors
                            )
                            session.add(favorite)
                            session.commit()
                        except Exception as e:
                            print(f"Failed due to {str(e)}")
                            session.rollback()


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 favorite.py <file_name> <chunk_number>")
        sys.exit(1)

    file_name = sys.argv[1]
    chunk_number = int(sys.argv[2])
    customer = migrateFavorite(file_name, chunk_number)
    customer.migrate_favorite()
