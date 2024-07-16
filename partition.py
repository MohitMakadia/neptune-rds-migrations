from utils.connect import neptune_connect
from gremlin_python.structure.graph import Graph
import os
import sys


class PartChunks:

    def __init__(self, file_name, total_chunks, label):
        self.neptune_engine = neptune_connect()
        self.g = Graph().traversal().withRemote(self.neptune_engine)
        self.file_name = file_name
        self.chunks = total_chunks
        self.label = label

    def part_chunks(self):
        all_vertex_ids = [v.id for v in self.g.V().hasLabel(self.label).toList()]
        chunk_size = self.chunks
        chunks = {}

        for i in range(0, len(all_vertex_ids), chunk_size):
            chunk_ids = all_vertex_ids[i : i + chunk_size]
            chunks[i // chunk_size + 1] = chunk_ids

        chunks_folder = "chunks"
        if not os.path.exists(chunks_folder):
            os.makedirs(chunks_folder)

        with open("chunks/" + self.file_name, "w") as f:
            f.write(str(chunks))


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python3 partition.py <file_name> <chunk_number> <label>")
        sys.exit(1)

    file_name = sys.argv[1]
    total_chunks = int(sys.argv[2])
    label = sys.argv[3]
    part_chunks = PartChunks(file_name, total_chunks, label)
    part_chunks.part_chunks()
