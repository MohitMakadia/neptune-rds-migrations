# type: ignore[import]
from __future__ import print_function
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from gremlin_python.structure.graph import Graph
from gremlin_python.driver.driver_remote_connection import DriverRemoteConnection

load_dotenv()
graph = Graph()

# RDS
hostname = os.getenv("RDS_HOST")
username = os.getenv("RDS_USERID")
password = os.getenv("RDS_PASSWORD")
port = os.getenv("RDS_PORT")
database = os.getenv("RDS_DATABASE")

# NEPTUNE
neptuneEndpoint = os.getenv("NEPTUNE_ENDPOINT")
neptunePort = os.getenv("NEPTUNE_PORT")


def rds_connect():
    database_url = f"postgresql://{username}:{password}@{hostname}:{port}/{database}"
    return create_engine(database_url)


def neptune_connect():
    return DriverRemoteConnection(f"wss://{neptuneEndpoint}:{neptunePort}/gremlin", "g")
