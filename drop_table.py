# from app import create_app
# from models import db, Suspect

# app = create_app()

# with app.app_context():
#     Suspect.__table__.drop(db.engine)
#     print("Suspect table dropped.")


from app import create_app
from models import db, CCTV

app = create_app()

with app.app_context():
    print("Dropping CCTV table...")
    CCTV.__table__.drop(db.engine)
    print("Creating tables again...")
    db.create_all()
    print("Done.")