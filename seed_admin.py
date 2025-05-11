# seed_admin.py

from app import create_app
from models import db, User

# Boot up your Flask app context
app = create_app()
with app.app_context():
    # Check if 'admin' already exists
    if User.query.filter_by(username='admin').first():
        print("✅ Admin user already exists")
    else:
        # Create it with password 'secret'
        u = User(username='admin', role='admin')
        u.set_password('secret')
        db.session.add(u)
        db.session.commit()
        print("✅ Created admin / secret")
