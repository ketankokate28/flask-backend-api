from models import db, Tenant, Node
from flask import Flask
from datetime import datetime

app = Flask(__name__)
app.config.from_object('config.Config')
db.init_app(app)

states = [
    {
        "name": "Maharashtra",
        "districts": [
            {"name": "Ahmednagar"},
            {"name": "Akola"},
            {"name": "Amravati"},
            {"name": "Aurangabad"},
            {"name": "Beed"},
            {"name": "Bhandara"},
            {"name": "Buldhana"},
            {"name": "Chandrapur"},
            {"name": "Dhule"},
            {"name": "Gadchiroli"},
            {"name": "Gondia"},
            {"name": "Hingoli"},
            {"name": "Jalgaon"},
            {"name": "Jalna"},
            {"name": "Kolhapur"},
            {"name": "Latur"},
            {"name": "Mumbai City"},
            {"name": "Mumbai Suburban"},
            {"name": "Nagpur"},
            {"name": "Nanded"},
            {"name": "Nandurbar"},
            {"name": "Nashik"},
            {"name": "Osmanabad"},
            {"name": "Palghar"},
            {"name": "Parbhani"},
            {"name": "Pune"},
            {"name": "Raigad"},
            {"name": "Ratnagiri"},
            {"name": "Sangli"},
            {"name": "Satara"},
            {"name": "Sindhudurg"},
            {"name": "Solapur"},
            {"name": "Thane"},
            {"name": "Wardha"},
            {"name": "Washim"},
            {"name": "Yavatmal"}
        ]
    },
    {
        "name": "Gujarat",
        "districts": [
            {"name": "Ahmedabad"},
            {"name": "Amreli"},
            {"name": "Anand"},
            {"name": "Aravalli"},
            {"name": "Banaskantha"},
            {"name": "Bharuch"},
            {"name": "Bhavnagar"},
            {"name": "Botad"},
            {"name": "Chhota Udaipur"},
            {"name": "Dahod"},
            {"name": "Dang"},
            {"name": "Devbhoomi Dwarka"},
            {"name": "Gandhinagar"},
            {"name": "Gir Somnath"},
            {"name": "Jamnagar"},
            {"name": "Junagadh"},
            {"name": "Kheda"},
            {"name": "Kutch"},
            {"name": "Mehsana"},
            {"name": "Morbi"},
            {"name": "Narmada"},
            {"name": "Navsari"},
            {"name": "Panchmahal"},
            {"name": "Patan"},
            {"name": "Porbandar"},
            {"name": "Rajkot"},
            {"name": "Sabarkantha"},
            {"name": "Surat"},
            {"name": "Surendranagar"},
            {"name": "Tapi"},
            {"name": "Vadodara"},
            {"name": "Valsad"}
        ]
    }
]

with app.app_context():
    for state in states:
        tenant = Tenant(name=state["name"], created_at=datetime.utcnow())
        db.session.add(tenant)
        db.session.flush()  # get tenant.id
        print(f"Inserted Tenant: {tenant.name} (id={tenant.id})")

        for district in state["districts"]:
            node = Node(name=district["name"], tenant_id=tenant.id, created_at=datetime.utcnow())
            db.session.add(node)
            print(f"    Inserted Node: {node.name} (tenant_id={tenant.id})")

    db.session.commit()
    print("✅ Seeding completed.")
