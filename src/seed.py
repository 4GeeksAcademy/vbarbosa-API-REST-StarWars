from app import app, db
from models import User, Favorite, Planet, People, FavPeople, FavPlanet

with app.app_context():
    db.drop_all()
    db.create_all()

    #Create users and fovourite list
    new_user1 = User(name="vicky", last_name="barbosa", email= "vb@gmail.com", password="123456789")
    new_user2 = User(name="lola", last_name="Lopez", email= "ll@gmail.com", password="123456789")
    db.session.add_all([new_user1, new_user2])
    db.session.commit()

    fav1 = Favorite(user_id=new_user1.id)
    fav2 = Favorite(user_id=new_user2.id)
    db.session.add_all([fav1, fav2])
    db.session.commit()

    #Create planets and add to fav list
    planets1 = Planet(name_planet="Marte")
    planets2 = Planet(name_planet="Jupiter")
    db.session.add_all([planets1, planets2])
    db.session.commit()

    planet_fav1 = FavPlanet(fav_id=fav1.id, planet_id=planets1.id)
    planet_fav2 = FavPlanet(fav_id=fav2.id, planet_id=planets2.id)
    db.session.add_all([planet_fav1, planet_fav2])

    #Create people and add to fav list
    people1 = People(name_people="Juan Junior")
    people2 = People(name_people="Pepe Junior")
    db.session.add_all([people1, people2])
    db.session.commit()

    people_fav1 = FavPeople(fav_id=fav1.id, people_id=people1.id)
    people_fav2 = FavPeople(fav_id=fav2.id, people_id=people2.id)
    db.session.add_all([people_fav1, people_fav2])

    db.session.commit()
