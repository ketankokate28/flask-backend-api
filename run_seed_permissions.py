from app import create_app
from models import db, Permission

app = create_app()

def seed_permissions():
    perms = [
        Permission(name='View Users', value='users.view', group_name='Users', description='Can view users'),
        Permission(name='Manage Users', value='users.manage', group_name='Users', description='Can manage users'),
        Permission(name='View Roles', value='roles.view', group_name='Roles', description='Can view roles'),
        Permission(name='Manage Roles', value='roles.manage', group_name='Roles', description='Can manage roles'),
        Permission(name='Assign Roles', value='roles.assign', group_name='Roles', description='Can assign roles'),
    ]
    with app.app_context():
        db.session.bulk_save_objects(perms)
        db.session.commit()
        print("✅ Permissions seeded successfully.")

if __name__ == '__main__':
    seed_permissions()

## to add permissions in DB run: python run_seed_permissions.py