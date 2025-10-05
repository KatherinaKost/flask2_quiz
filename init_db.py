# init_db.py
from main import app, db, add_data

if __name__ == '__main__':
    with app.app_context():
        add_data()
        