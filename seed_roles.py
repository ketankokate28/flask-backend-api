from app import create_app
from models import db, Role, Permission

from uuid import uuid4

app = create_app()

def seed_roles():
    with app.app_context():
        # Fetch permissions to assign
        all_permissions = Permission.query.all()
        perm_dict = {perm.value: perm for perm in all_permissions}

        # Define roles and associated permission values
        roles_data = [
            {
                'name': 'admin',
                'description': 'Administrator with full access',
                'permissions': list(perm_dict.values())  # all permissions
            },
            {
                'name': 'user',
                'description': 'Regular user with limited access',
                'permissions': [
                    perm_dict.get('users.view'),
                    perm_dict.get('roles.view')
                ]
            }
        ]

        for role_data in roles_data:
            existing = Role.query.filter_by(name=role_data['name']).first()
            if not existing:
                role = Role(
                    id=str(uuid4()),
                    name=role_data['name'],
                    description=role_data['description']
                )
                role.permissions = [p for p in role_data['permissions'] if p is not None]
                db.session.add(role)

        db.session.commit()
        print("✅ Roles seeded successfully.")

if __name__ == '__main__':
    seed_roles()
