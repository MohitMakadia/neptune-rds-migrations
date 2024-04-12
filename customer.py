# type: ignore[import]
from models.Customer import Customer, Base
from utils.connect import rdsConnect, neptuneConnect
from gremlin_python.structure.graph import Graph
from sqlalchemy import inspect
from utils.rdsSession import createRdsSession, commitRds
import uuid


class migrateCustomer:
    
    def __init__(self):
        self.engine = rdsConnect()
        self.neptune_engine = neptuneConnect()
        self.g = Graph().traversal().withRemote(self.neptune_engine)
        self.table = "Customer"
              
    def checkIfTableExists(self):
        inspector = inspect(self.engine)
        if self.table in inspector.get_table_names():
            print(f'Table {self.table} exists.')
        else:
            print(f'Table {self.table} does not exist.')

    def createCustomerTable(self):
        print(f'Creating {self.table} Table ...')
        Customer.tableLaunch()
        print(f'{self.table} Table Created')

    def validate_uuid(self, uuid_str):
        try:
            uuid.UUID(uuid_str)
            return True
        except ValueError:
            return False

    def migrateCustomer(self):
        self.checkIfTableExists()
        self.createCustomerTable()
        print(f'Starting Migration for {self.table} table ...')
        vertexIds = self.g.V().hasLabel("customer").toList()
        for vertexId in vertexIds:
            if self.validate_uuid(vertexId.id):
                customerValueMaps = self.g.V(vertexId).valueMap().toList()
                for customerValueMap in customerValueMaps:
                    Base.metadata.bind = self.engine
                    session = createRdsSession()
                    try:
                        customer = Customer(
                            customer_id = vertexId.id,
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
                print(f'Invalid UUID Detected {vertexId.id} ... Skipping.')

customer = migrateCustomer()
customer.migrateCustomer()