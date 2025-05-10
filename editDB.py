from __init__ import app, db, Item, User

item1 = Item(name="iphone 10", price=500, barcode="8241475129", description="desc")
item2 = Item(name="Laptop", price=700, barcode="231491818", description="description")
user1 = User(username="test", email_address="dnajwf@gmail.com", password_hash="123456")


with app.app_context():
    db.session.add(item2)
    db.session.commit()

    # item1.owner = User.query.filter_by(username='test').first().id

    # db.session.add(item1)
    # db.session.commit()