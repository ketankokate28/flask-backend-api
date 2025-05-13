pip show flask
pip install flask
pip install flask-migrate
.\venv\Scripts\Activate.ps1
flask db init
flask db migrate -m "initial"


pip install Flask-Migrate
flask db init
flask db migrate -m "Add jobTitle and other new fields to User"
flask db upgrade

## If still error then start with this command  python clear_alembic.py

python run_seed_permissions.py
python seed_roles.py     

************ Clean git cache*****
git rm -r --cached .
git add .
git commit -m "Fix: stop tracking ignored files"

**********************************