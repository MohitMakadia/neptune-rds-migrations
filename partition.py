from utils.connect import neptuneConnect
from gremlin_python.structure.graph import Graph
import os

class PartChunks:

    def __init__(self, file_name, chunks):
        self.neptune_engine = neptuneConnect()
        self.g = Graph().traversal().withRemote(self.neptune_engine)
        self.file_name = file_name
        self.chunks = chunks
        
    def partChunks(self):
        allVertexIds = [v.id for v in self.g.V().hasLabel('worker').toList()]
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

part_chunks = PartChunks("worker.txt", 200)
part_chunks.partChunks()