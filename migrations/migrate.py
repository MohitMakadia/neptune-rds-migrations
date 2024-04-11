# type: ignore[import]
from connect import rdsConnect, neptuneConnect
from gremlin_python.structure.graph import Graph
from sqlalchemy import inspect
from customerSchema import Customer, Base
from workerSchema import Worker, Base
from rdsSession import createRdsSession, commitRds
import uuid

class RDS:
    
    def __init__(self, tableName):
        self.engine = rdsConnect()
        self.neptune_engine = neptuneConnect()
        self.g = Graph().traversal().withRemote(self.neptune_engine)
        self.table = tableName
              
    def checkIfTableExists(self):
        inspector = inspect(self.engine)
        if self.table in inspector.get_table_names():
            print(f'Table {self.table} exists.')
        else:
            print(f'Table {self.table} does not exist.')
            self.createCustomerTable()

    def createCustomerTable(self):
        print(f'Creating {self.table} Table ...')
        Customer.tableLaunch()
        print(f'{self.table} Created')

    def validate_uuid(self, uuid_str):
        try:
            uuid.UUID(uuid_str)
            return True
        except ValueError:
            return False

    def migrateCustomer(self):
        self.checkIfTableExists()
        print(f'Starting Migration for {self.table} table ...')
        vertedIds = self.g.V().hasLabel("customer").toList()
        for vertedId in vertedIds:
            if self.validate_uuid(vertedId.id):
                customerValueMaps = self.g.V(vertedId).valueMap().toList()
                for customerValueMap in customerValueMaps:
                    Base.metadata.bind = self.engine
                    session = createRdsSession()
                    try:
                        customer = Customer(
                            customer_id = vertedId.id,
                            amount = customerValueMap.get("amount", [0])[0],
                            domain_language = customerValueMap.get("domain_language", [""])[0],
                            domain = customerValueMap.get("domain", [""])[0],
                            duration = customerValueMap.get("duration", [0])[0],
                            email = customerValueMap.get("email", [""])[0],
                            experience = customerValueMap.get("experience", [0])[0],
                            first_name = customerValueMap.get("first_name", [""])[0],
                            internal_score = customerValueMap.get("internal_score", [0])[0],
                            interval = customerValueMap.get("interval", [0])[0],
                            is_deleted = customerValueMap.get("is_deleted", [False])[0],
                            is_online = customerValueMap.get("is_online", [False])[0],
                            is_suspended = customerValueMap.get("is_suspended", [False])[0],
                            last_login = customerValueMap.get("last_login", [0])[0],
                            location_address = customerValueMap.get("location_address", [""])[0],
                            location_city = customerValueMap.get("location_city", [""])[0],
                            location_country = customerValueMap.get("location_country", [""])[0],
                            location_place_id = customerValueMap.get("location_place_id", [""])[0],
                            location_slug = customerValueMap.get("location_slug", [""])[0],
                            personal_note = customerValueMap.get("personal_note", [""])[0],
                            phone_no = customerValueMap.get("phone_no", [""])[0],
                            profile_picture = customerValueMap.get("profile_picture", [""])[0],
                            published = customerValueMap.get("published", [False])[0],
                            registered_date = customerValueMap.get("registered_date", [0])[0],
                            score = customerValueMap.get("score", [0])[0],
                            user_alert = customerValueMap.get("user_alert", [False])[0],
                            votes = customerValueMap.get("votes", [0])[0],
                            location_longitude = customerValueMap.get("location_longitude", [0.0])[0],
                            location_latitude = customerValueMap.get("location_latitude", [0.0])[0],
                            max_distance = customerValueMap.get("max_distance", [0])[0]
                            )
                        session.add(customer)
                        commitRds(session)
                    except Exception as e:
                        print(str(e))
                        session.close()
            else:
                print(f'Invalid UUID Detected {vertedId.id} ... Skipping.')

    def migrateWorker(self):
        self.checkIfTableExists()
        with createRdsSession() as session:
            vertedIds = self.g.V().hasLabel("worker").toList()
            for vertedId in vertedIds:
                workerValueMaps = self.g.V(vertedId).valueMap().toList()
                for workerValueMap in workerValueMaps:
                    Base.metadata.bind = self.engine
                    session = createRdsSession()
                    worker = Worker(
                        worker_id = vertedId.id,
                        amount = workerValueMap.get("amount", [0])[0],
                        domain_language = workerValueMap.get("domain_language", [""])[0],
                        domain = workerValueMap.get("domain", [""])[0],
                        email = workerValueMap.get("email", [""])[0],
                        experience = workerValueMap.get("experience", [0])[0],
                        first_name = workerValueMap.get("first_name", [""])[0],
                        internal_score = workerValueMap.get("internal_score", [0])[0],
                        is_online = workerValueMap.get("is_online", [False])[0],
                        is_suspended = workerValueMap.get("is_suspended", [False])[0],
                        last_login = workerValueMap.get("last_login", [0])[0],
                        location_address = workerValueMap.get("location_address", [""])[0],
                        location_city = workerValueMap.get("location_city", [""])[0],
                        location_country = workerValueMap.get("location_country", [""])[0],
                        location_longitude = workerValueMap.get("location_longitude", [0.0])[0],
                        location_latitude = workerValueMap.get("location_latitude", [0.0])[0],
                        location_place_id = workerValueMap.get("location_place_id", [""])[0],
                        location_slug = workerValueMap.get("location_slug", [""])[0],
                        max_distance = workerValueMap.get("max_distance", [0])[0],
                        personal_note = workerValueMap.get("personal_note", [""])[0],
                        profile_picture = workerValueMap.get("profile_picture", [""])[0],
                        published = workerValueMap.get("published", [False])[0],
                        registered_date = workerValueMap.get("registered_date", [0])[0],
                        score = workerValueMap.get("score", [0])[0],
                        user_alert = workerValueMap.get("user_alert", [False])[0],
                        votes = workerValueMap.get("votes", [0])[0],
                        )
                    session.add(worker)
                    commitRds(session)

rds = RDS("Customer")
rds.migrateCustomer()


