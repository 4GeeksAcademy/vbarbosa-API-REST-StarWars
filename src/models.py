from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Boolean, ForeignKey, Column, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship

db = SQLAlchemy()

profile_planet = Table(
    "profile_planet",
    db.metadata,
    Column("profile_id", ForeignKey("profiles.id"), primary_key=True),
    Column("planet_id", ForeignKey("planets.id"), primary_key=True)
)

profile_people = Table(
    "profile_people",
    db.metadata,
    Column("profile_id", ForeignKey("profiles.id"), primary_key=True),
    Column("people_id", ForeignKey("peoples.id"), primary_key=True)
)

class User(db.Model):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)

    # relationship with other tables
    profile: Mapped["Profile"] = relationship(back_populates="user", uselist=False)

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            # do not serialize the password, its a security breach
        }
    

class Profile(db.Model):
    __tablename__ = "profiles"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
        
    # relationship with other tables
    user: Mapped["User"] = relationship(back_populates="profile")
    planets: Mapped[list["Planet"]] = relationship(secondary="profile_planet", back_populates="profiles")
    peoples: Mapped[list["People"]] = relationship(secondary="profile_people", back_populates="profiles")

    def serialize(self):
        return {
            "id": self.id,
            "Favourite Planets": [planet.name_planet for planet in self.planets],
            "Favourite People": [people.name_people for people in self.peoples]
        }

class Planet(db.Model):

    __tablename__ = "planets"
    id: Mapped[int] = mapped_column(primary_key=True)
    name_planet: Mapped[str] = mapped_column(String(100), unique=True)

    # relationship with other tables
    profiles: Mapped["Profile"] = relationship(secondary="profile_planet", back_populates="planets")

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
    profiles: Mapped["Profile"] = relationship(secondary="profile_people", back_populates="peoples")

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name_people
        }
