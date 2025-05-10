from __init__ import app, db, DataScraping, User

with app.app_context():
    print(DataScraping.query.all())
    print("\n")

    for ds in DataScraping.query.all():
        print(ds.id)
        print(ds.link)
        print(ds.prompt)
        print(ds.response)
        print(ds.owner_username)
    
    
    print("\n")
    print(User.query.all())