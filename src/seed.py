from app import app, db
from models import User, Profile, Planet, People

with app.app_context():
    db.drop_all()
    db.create_all()

    new_user = User(email= "vbarbosa@gmail.com", password="123456789")
    db.session.add_all([new_user])
    db.session.commit()
    print(new_user.id)