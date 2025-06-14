from app import create_app, db
from cctv import CCTV  # Replace with the actual model

# Create app instance
app = create_app()

# Run the delete operation within an application context
with app.app_context():
    # Delete all records from the table
    try:
        db.session.query(CCTV).delete()
        db.session.commit()  # Commit the transaction to the database
        print(f"All records from {CCTV.__tablename__} have been deleted.")
    except Exception as e:
        db.session.rollback()  # In case of an error, rollback the transaction
        print(f"An error occurred: {e}")
