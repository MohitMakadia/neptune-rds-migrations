# type: ignore[import]
from models.Day import Day, Base
from utils.connect import rdsConnect, neptuneConnect
from gremlin_python.structure.graph import Graph
from sqlalchemy import inspect
from utils.session import createRdsSession, commitRds
from utils.validation import validate_uuid, checkIfTableExists
import ast
import os

class migrateDay:
    
    def __init__(self):
        self.engine = rdsConnect()
        self.neptune_engine = neptuneConnect()
        self.g = Graph().traversal().withRemote(self.neptune_engine)
        self.table = "Day"
              
    def createDayTable(self):
        print(f'Creating {self.table} Table ...')
        Day.tableLaunch()
        print(f'{self.table} Table Created')

    def processChunks(self, key):
        input_file = "day.txt"
        with open("chunks/" + input_file, "r") as f:
            chunks_str = f.read()

        chunks = ast.literal_eval(chunks_str)
        for k, v in chunks.items():
            if k == key:
                return k, v
    
        return None, None
    
    def markChunkCompleted(self, chunk_num, status):

        chunks_folder = "chunks/day_status"
        if not os.path.exists(chunks_folder):
            os.makedirs(chunks_folder)
        
        completed_file = f"chunks/day_status/completed_{chunk_num}.txt"
        
        with open(completed_file, "w") as f:
            f.write(str({chunk_num: [status]}))
    
    def migrateDay(self):
        checkIfTableExists(self.engine, self.table)
        self.createDayTable()
        print(f'Starting Migration for {self.table} table ...')
        Base.metadata.bind = self.engine
        chunk_name, chunk_data = self.processChunks(1)
        print("Chunk -> ", chunk_name)
        session = createRdsSession()
        try:
            for vertexId in chunk_data:
                workers_to_add = []
                daysValueMap = self.g.V(vertexId).valueMap().toList()[0]
                outVertexs = self.g.V(vertexId).outE().toList()
                for outVertex in outVertexs:
                    try:
                        outVertexId = str(outVertex).split("][")[1].split("->")[1][:-1]
                        day = Day(
                            day_id = vertexId,
                            day_name = daysValueMap.get("day_name", [None])[0],
                            day_of_week = daysValueMap.get("day_of_week", [None])[0],
                            last_login = daysValueMap.get("last_login", [None])[0],
                            is_working_day_for = outVertexId
                        )
                        workers_to_add.append(day)

                    except Exception as e:
                        print(f'Failed due to {str(e)}')

                session.add_all(workers_to_add)

            session.commit()
        
        except Exception as e:
            print(str(e))
            session.rollback()
        
        finally:
            session.close()

worker = migrateDay()
worker.migrateDay()