# type: ignore[import]
from models.Customer import Customer, Base
from utils.connect import rdsConnect, neptuneConnect
from gremlin_python.structure.graph import Graph
from utils.session import createRdsSession
from utils.validation import checkIfTableExists
import sys
import ast
import os


class migrateCustomer:

    def __init__(self, chunk_number):
        self.engine = rdsConnect()
        self.neptune_engine = neptuneConnect()
        self.g = Graph().traversal().withRemote(self.neptune_engine)
        self.table = "NewCustomer"
        self.chunk_number = chunk_number

    def createCustomerTable(self):
        print(f'Creating {self.table} Table ...')
        Customer.tableLaunch()
        print(f'{self.table} Table Created')

    def processChunks(self, key):
        input_file = "customer.txt"
        with open("chunks/" + input_file, "r") as f:
            chunks_str = f.read()

        chunks = ast.literal_eval(chunks_str)
        for k, v in chunks.items():
            if k == key:
                return k, v

        return None, None

    def markChunkCompleted(self, chunk_num, status):

        chunks_folder = "chunks/customer_status"
        if not os.path.exists(chunks_folder):
            os.makedirs(chunks_folder)

        completed_file = f"chunks/customer_status/completed_{chunk_num}.txt"

        with open(completed_file, "w") as f:
            f.write(str({chunk_num: [status]}))

    def migrateCustomer(self):
        checkIfTableExists(self.engine, self.table)
        self.createCustomerTable()
        print(f'Starting Migration for {self.table} table ...')
        Base.metadata.bind = self.engine
        # vertexIds = self.g.V().hasLabel("customer").toList()
        chunk_name, chunk_data = self.processChunks(self.chunk_number)
        session = createRdsSession()
        for vertexId in chunk_data:
            customerValueMap = self.g.V(vertexId).valueMap().toList()[0]
            outEdges = self.g.V(vertexId).outE().toList()

            verified_by = None
            participates_in = None
            authored = None
            speaks = None
            wants_to_pay_in = None
            wants_service_on = None
            favored_by = None
            receives = None
            issued = None
            favors = None
            is_evaluated_by = None
            wrote = None
            wants_payment_in = None
            works_on = None
            requires_handling = None

            for edge in outEdges:

                outVertexId = str(edge).split("][")[1].split("->")[1][:-1]

                if edge.label == "verified_by":
                    verified_by = outVertexId

                if edge.label == "participates_in":
                    participates_in = outVertexId

                if edge.label == "authored":
                    authored = outVertexId

                if edge.label == "speaks":
                    speaks = outVertexId

                if edge.label == "wants_to_pay_in":
                    wants_to_pay_in = outVertexId

                if edge.label == "wants_service_on":
                    wants_service_on = outVertexId

                if edge.label == "favored_by":
                    favored_by = outVertexId

                if edge.label == "receives":
                    receives = outVertexId

                if edge.label == "issued":
                    issued = outVertexId

                if edge.label == "favors":
                    favors = outVertexId

                if edge.label == "is_evaluated_by":
                    is_evaluated_by = outVertexId

                if edge.label == "wrote":
                    wrote = outVertexId

                if edge.label == "wants_payment_in":
                    wants_payment_in = outVertexId

                if edge.label == "works_on":
                    works_on = outVertexId

                if edge.label == "requires_handling":
                    requires_handling = outVertexId

                try:
                    customer = Customer(
                        customer_id=vertexId,  # vertexId.id
                        amount=customerValueMap.get("amount", [None])[0],
                        domain_language=customerValueMap.get(
                            "domain_language", [None])[0],
                        domain=customerValueMap.get("domain", [None])[0],
                        duration=customerValueMap.get("duration", [None])[0],
                        email=customerValueMap.get("email", [None])[0],
                        experience=customerValueMap.get(
                            "experience", [None])[0],
                        first_name=customerValueMap.get(
                            "first_name", [None])[0],
                        internal_score=customerValueMap.get(
                            "internal_score", [None])[0],
                        interval=customerValueMap.get("interval", [None])[0],
                        is_deleted=customerValueMap.get(
                            "is_deleted", [None])[0],
                        is_online=customerValueMap.get("is_online", [None])[0],
                        is_suspended=customerValueMap.get(
                            "is_suspended", [None])[0],
                        last_login=customerValueMap.get(
                            "last_login", [None])[0],
                        location_address=customerValueMap.get(
                            "location_address", [None])[0],
                        location_city=customerValueMap.get(
                            "location_city", [None])[0],
                        location_country=customerValueMap.get(
                            "location_country", [None])[0],
                        location_place_id=customerValueMap.get(
                            "location_place_id", [None])[0],
                        location_slug=customerValueMap.get(
                            "location_slug", [None])[0],
                        personal_note=customerValueMap.get(
                            "personal_note", [None])[0],
                        phone_no=customerValueMap.get("phone_no", [None])[0],
                        profile_picture=customerValueMap.get(
                            "profile_picture", [None])[0],
                        published=customerValueMap.get("published", [None])[0],
                        registered_date=customerValueMap.get(
                            "registered_date", [None])[0],
                        score=customerValueMap.get("score", [None])[0],
                        user_alert=customerValueMap.get(
                            "user_alert", [None])[0],
                        votes=customerValueMap.get("votes", [None])[0],
                        location_longitude=customerValueMap.get(
                            "location_longitude", [None])[0],
                        location_latitude=customerValueMap.get(
                            "location_latitude", [None])[0],
                        max_distance=customerValueMap.get(
                            "max_distance", [None])[0],
                        verified_by=verified_by,
                        participates_in=participates_in,
                        authored=authored,
                        speaks=speaks,
                        wants_to_pay_in=wants_to_pay_in,
                        wants_service_on=wants_service_on,
                        favored_by=favored_by,
                        receives=receives,
                        issued=issued,
                        favors=favors,
                        is_evaluated_by=is_evaluated_by,
                        wrote=wrote,
                        wants_payment_in=wants_payment_in,
                        works_on=works_on,
                        requires_handling=requires_handling
                    )

                    session.add(customer)
                    session.commit()

                except Exception as e:
                    print(f'Failed due to {str(e)}')
                    session.rollback()

        self.markChunkCompleted(chunk_name, "Completed")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 customer.py <chunk_number>")
        sys.exit(1)

    chunk_number = int(sys.argv[1])
    customer = migrateCustomer(chunk_number)
    customer.migrateCustomer()
