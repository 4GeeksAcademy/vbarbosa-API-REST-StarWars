from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    last_name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)

    # relationship with other tables
    favorites: Mapped[list["Favorite"]] = relationship(back_populates="user")

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "last name": self.last_name,
            "email": self.email,
            "favorites": [fav.serialize() for fav in self.favorites]
            # do not serialize the password, its a security breach
        }
    

class Favorite(db.Model):
    __tablename__ = "favorites"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
        
    # relationship with other tables
    user: Mapped["User"] = relationship(back_populates="favorites")
    planets: Mapped[list["FavPlanet"]] = relationship(back_populates="favorite")
    peoples: Mapped[list["FavPeople"]] = relationship(back_populates="favorite")

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "favorite_planets": [planet.serialize() for planet in self.planets],
            "favorite_people": [people.serialize() for people in self.peoples]
        }

class FavPlanet(db.Model):
    __tablename__ = "fav_planets"
    fav_id: Mapped[int] = mapped_column(ForeignKey("favorites.id"), primary_key=True)
    planet_id: Mapped[int] = mapped_column(ForeignKey("planets.id"), primary_key=True)

   # relationship with other tables
    planet: Mapped["Planet"] = relationship(back_populates="fav_planet") #child
    favorite: Mapped["Favorite"] = relationship(back_populates="planets") #parent

    def serialize(self):
        return {
            "fav_id":self.fav_id,
            "planet_id": self.planet_id,
            "planet_name": self.planet.name_planet
        }
    
class FavPeople(db.Model):
    __tablename__ = "fav_people"
    fav_id: Mapped[int] = mapped_column(ForeignKey("favorites.id"), primary_key=True)
    people_id: Mapped[int] = mapped_column(ForeignKey("peoples.id"), primary_key=True)


   # relationship with other tables
    people: Mapped["People"] = relationship(back_populates="fav_people") #child
    favorite: Mapped["Favorite"] = relationship(back_populates="peoples") #parent

    def serialize(self):
        return {
            "fav_id":self.fav_id,
            "people_id": self.people_id,
            "people_name": self.people.name_people
        }
    

class Planet(db.Model):
    __tablename__ = "planets"
    id: Mapped[int] = mapped_column(primary_key=True)
    name_planet: Mapped[str] = mapped_column(String(100), unique=True)

    # relationship with other tables
    fav_planet: Mapped[list["FavPlanet"]] = relationship(back_populates="planet")

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name_planet
        }
    
class People(db.Model):
    __tablename__ = "peoples"
    id: Mapped[int] = mapped_column(primary_key=True)
    name_people: Mapped[str] = mapped_column(String(100), unique=True)

   # relationship with other tables
    fav_people: Mapped[list["FavPeople"]] = relationship(back_populates="people")

    def serialize(self):
        return {
            "id": self.id,
            "name_people": self.name_people
        }
