from __init__ import app, db

with app.app_context():
    db.drop_all()