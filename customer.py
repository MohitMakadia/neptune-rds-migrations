# type: ignore[import]
from models.Customer import Customer, Base
from utils.connect import rdsConnect, neptuneConnect
from gremlin_python.structure.graph import Graph
from sqlalchemy import inspect
from utils.session import createRdsSession, commitRds
from utils.validation import validate_uuid, checkIfTableExists

class migrateCustomer:
    
    def __init__(self):
        self.engine = rdsConnect()
        self.neptune_engine = neptuneConnect()
        self.g = Graph().traversal().withRemote(self.neptune_engine)
        self.table = "Customer"
              
    def createCustomerTable(self):
        print(f'Creating {self.table} Table ...')
        Customer.tableLaunch()
        print(f'{self.table} Table Created')

    def migrateCustomer(self):
        checkIfTableExists(self.engine, self.table)
        self.createCustomerTable()
        print(f'Starting Migration for {self.table} table ...')
        Base.metadata.bind = self.engine
        vertexIds = self.g.V().hasLabel("customer").toList()
        for vertexId in vertexIds:
            customerValueMap = self.g.V(vertexId).valueMap().toList()[0]
            outEdges = self.g.V(vertexId).outE().toList()
            for edge in outEdges:
                session = createRdsSession()
                try:
                    outVertexId = str(edge).split("][")[1].split("->")[1][:-1]
                    customer = Customer(
                        customer_id = vertexId.id,
                        amount = customerValueMap.get("amount", [None])[0],
                        domain_language = customerValueMap.get("domain_language", [None])[0],
                        domain = customerValueMap.get("domain", [None])[0],
                        duration = customerValueMap.get("duration", [None])[0],
                        email = customerValueMap.get("email", [None])[0],
                        experience = customerValueMap.get("experience", [None])[0],
                        first_name = customerValueMap.get("first_name", [None])[0],
                        internal_score = customerValueMap.get("internal_score", [None])[0],
                        interval = customerValueMap.get("interval", [None])[0],
                        is_deleted = customerValueMap.get("is_deleted", [None])[0],
                        is_online = customerValueMap.get("is_online", [None])[0],
                        is_suspended = customerValueMap.get("is_suspended", [None])[0],
                        last_login = customerValueMap.get("last_login", [None])[0],
                        location_address = customerValueMap.get("location_address", [None])[0],
                        location_city = customerValueMap.get("location_city", [None])[0],
                        location_country = customerValueMap.get("location_country", [None])[0],
                        location_place_id = customerValueMap.get("location_place_id", [None])[0],
                        location_slug = customerValueMap.get("location_slug", [None])[0],
                        personal_note = customerValueMap.get("personal_note", [None])[0],
                        phone_no = customerValueMap.get("phone_no", [None])[0],
                        profile_picture = customerValueMap.get("profile_picture", [None])[0],
                        published = customerValueMap.get("published", [None])[0],
                        registered_date = customerValueMap.get("registered_date", [None])[0],
                        score = customerValueMap.get("score", [None])[0],
                        user_alert = customerValueMap.get("user_alert", [None])[0],
                        votes = customerValueMap.get("votes", [None])[0],
                        location_longitude = customerValueMap.get("location_longitude", [None])[0],
                        location_latitude = customerValueMap.get("location_latitude", [None])[0],
                        max_distance = customerValueMap.get("max_distance", [None])[0],
                        verified_by = None,
                        participates_in = None,
                        authored = None,
                        speaks = None,
                        wants_to_pay_in = None,
                        wants_service_on = None,
                        favored_by = None,
                        receives = None,
                        issued = None,
                        favors = None,
                        is_evaluated_by = None,
                        wrote = None,
                        wants_payment_in = None,
                        works_on = None,
                        requires_handling = None
                        )

                    if edge.label == "verified_by":
                        customer.verified_by = outVertexId

                    if edge.label == "participates_in":
                        customer.participates_in = outVertexId

                    if edge.label == "authored":
                        customer.authored = outVertexId
                    
                    if edge.label == "speaks":
                        customer.speaks = outVertexId
                    
                    if edge.label == "wants_to_pay_in":
                        customer.wants_to_pay_in = outVertexId
                    
                    if edge.label == "wants_service_on":
                        customer.wants_service_on = outVertexId

                    if edge.label == "favored_by":
                        customer.favored_by = outVertexId

                    if edge.label == "receives":
                        customer.receives = outVertexId
                        
                    if edge.label == "issued":
                        customer.issued = outVertexId

                    if edge.label == "favors":
                        customer.favors = outVertexId

                    if edge.label == "is_evaluated_by":
                        customer.is_evaluated_by = outVertexId

                    if edge.label == "wrote":
                        customer.wrote = outVertexId

                    if edge.label == "wants_payment_in":
                        customer.wants_payment_in = outVertexId

                    if edge.label == "works_on":
                        customer.works_on = outVertexId

                    if edge.label == "requires_handling":
                        customer.requires_handling =  outVertexId

                    session.add(customer)
                    commitRds(session)

                except Exception as e:
                    print(str(e))
                    session.close()
            
customer = migrateCustomer()
customer.migrateCustomer()