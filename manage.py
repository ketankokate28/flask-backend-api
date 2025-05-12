from flask import Flask
from app import create_app  # Or however you're creating your Flask app
from flask.cli import AppGroup

app = create_app()

seed_cli = AppGroup('seed')

@seed_cli.command('permission')
def seed_permissions():
    # call your seed logic here
    print("Seeding permissions...")

app.cli.add_command(seed_cli)

if __name__ == '__main__':
    app.run()

### to run this file for seed /.run command:   python manage.py seed permission
