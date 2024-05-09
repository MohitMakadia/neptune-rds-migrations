from utils.connect import neptuneConnect
from gremlin_python.structure.graph import Graph
import os
import sys

class PartChunks:

    def __init__(self, file_name, chunks, label):
        self.neptune_engine = neptuneConnect()
        self.g = Graph().traversal().withRemote(self.neptune_engine)
        self.file_name = file_name
        self.chunks = chunks
        self.label = label

    def partChunks(self):
        allVertexIds = [v.id for v in self.g.V().hasLabel(self.label).toList()]
        chunk_size = self.chunks
        chunks = {}

        for i in range(0, len(allVertexIds), chunk_size):
            chunk_ids = allVertexIds[i:i+chunk_size]
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
    chunks = int(sys.argv[2])
    label = sys.argv[3]
    part_chunks = PartChunks(file_name, chunks, label)
    part_chunks.partChunks()