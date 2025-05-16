"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from sqlalchemy import select
from models import db, User, Favorite, Planet, People, FavPeople, FavPlanet
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

# @app.route("/seed", methods=['GET'])
# def seed():

    ## Uncomment and paste below this line the seed file content
    ## It will create a trial database information for test


#     return jsonify("All data added successfully"), 200

# GET all users
@app.route('/users', methods=['GET'])
def get_users():

    statement = select(User)
    # el scalars() se ocupa de devolverlos como objeto, sino seran devueltos como tuplas.
    # como tupla NO pueden ejecutar el serialize

    users = db.session.execute(statement).scalars().all()

    return jsonify([user.serialize() for user in users]), 200

# GET only one user
@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):

    statement = select(User).where(User.id == user_id)
    user = db.session.execute(statement).scalar_one_or_none()

    if user is None:
        return jsonify({"error": "User not found"}), 404

    return jsonify(user.serialize()), 200

# GET all favorite for specific user
@app.route('/users/<int:user_id>/favorites', methods=['GET'])
def get_favorite(user_id):

    stmt_fav = select(Favorite).where(Favorite.user_id == user_id)
    favs = db.session.execute(stmt_fav).scalars().all()

    return jsonify([fav.serialize() for fav in favs]), 200

# GET all planets
@app.route('/planets', methods=['GET'])
def get_planets():

    statement = select(Planet)
    planets = db.session.execute(statement).scalars().all()

    return jsonify([planet.serialize() for planet in planets]), 200

# GET only one planet
@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_planet(planet_id):

    statement = select(Planet).where(Planet.id == planet_id)
    planet = db.session.execute(statement).scalar_one_or_none()

    if planet is None:
        return jsonify({"error": "Planet not found"}), 404

    return jsonify(planet.serialize()), 200

# GET all people
@app.route('/peoples', methods=['GET'])
def get_all_peoples():

    statement = select(People)
    peoples = db.session.execute(statement).scalars().all()

    return jsonify([people.serialize() for people in peoples]), 200

# GET only one people
@app.route('/peoples/<int:people_id>', methods=['GET'])
def get_person(people_id):

    statement = select(People).where(People.id == people_id)
    people = db.session.execute(statement).scalar_one_or_none()

    if people is None:
        return jsonify({"error": "Person not found"}), 404

    return jsonify(people.serialize()), 200

# GET all favorite planets of user
@app.route('/users/<int:user_id>/favorites/planets', methods=['GET'])
def get_fav_planets(user_id):

    statement = select(User).where(User.id == user_id)
    user = db.session.execute(statement).scalar_one_or_none()

    if user is None:
        return jsonify({"error": "User not found"}), 404

    statement = select(FavPlanet)
    fav = db.session.execute(statement).scalars().all()

    if fav is None:
        return jsonify({"error": "No favorite added"}), 404
    
    return jsonify([f.serialize() for f in fav]), 200

# GET all favorite people of user
@app.route('/users/<int:user_id>/favorites/peoples', methods=['GET'])
def get_fav_peoples(user_id):

    statement = select(User).where(User.id == user_id)
    user = db.session.execute(statement).scalar_one_or_none()

    if user is None:
        return jsonify({"error": "User not found"}), 404
    
    statement = select(FavPeople)
    fav = db.session.execute(statement).scalars().all()

    if fav is None:
        return jsonify({"error": "No favorite created"}), 404
    
    return jsonify([f.serialize() for f in fav]), 200

# Create user account
@app.route("/users", methods=["POST"])
def create_user():

    data = request.get_json()

    if not data or "email" not in data or "password" not in data or "name" not in data or "last_name" not in data:
        return jsonify({"error": "Missing data"}), 400
    
    new_user = User(
        name=data["name"],
        last_name=data["last_name"],
        email=data["email"],
        password=data["password"],
    )

    db.session.add(new_user)
    db.session.commit()

    return jsonify(new_user.serialize()), 201

# Create planet
@app.route("/planets", methods=["POST"])
def create_planet():

    data = request.get_json()

    if not data or "name_planet" not in data:
        return jsonify({"error": "Missing data"}), 400
    
    new_planet = Planet(
        name_planet=data["name_planet"]
    )
    db.session.add(new_planet)
    db.session.commit()

    return jsonify(new_planet.serialize()), 201

# Create people
@app.route("/peoples", methods=["POST"])
def create_people():

    data = request.get_json()

    if not data or "name_people" not in data:
        return jsonify({"error": "Missing data"}), 400
    
    new_people = People(
        name_people=data["name_people"]
    )
    db.session.add(new_people)
    db.session.commit()

    return jsonify(new_people.serialize()), 201

# Add planet to favorite list
@app.route("/users/<int:user_id>/favorites/planets/<int:planet_id>", methods=["POST"])
def add_fav_planet(user_id, planet_id):

    stmt_fav = select(Favorite).where(Favorite.user_id == user_id)
    fav = db.session.execute(stmt_fav).scalar_one_or_none()

    #We check if fav list was created otherwise we have to create a new one before adding planet to list
    if fav is None:
        fav = Favorite(user_id=user_id)
        db.session.add(fav)
        db.session.commit()

    #If fav list exists, we check if already exists has the planet we want to add
    stmt_planet = select(FavPlanet).where(
        FavPlanet.fav_id == fav.id,
        FavPlanet.planet_id == planet_id
        )
    fav_planet = db.session.execute(stmt_planet).scalar_one_or_none()

    #If found on the fav list, it returns an error
    if fav_planet is not None:
        return jsonify({"error": "Planet already added to list"}), 404
    
    #If not found on the fav list we add it
    new_fav_planet = FavPlanet(
        fav_id=fav.id,
        planet_id=planet_id
    )
    db.session.add(new_fav_planet)
    db.session.commit()

    return jsonify(new_fav_planet.serialize()), 201

# Add people to favorite list
@app.route("/users/<int:user_id>/favorites/peoples/<int:people_id>", methods=["POST"])
def add_fav_people(user_id, people_id):

    stmt_fav = select(Favorite).where(Favorite.user_id == user_id)
    fav = db.session.execute(stmt_fav).scalar_one_or_none()

    #We check if fav list was created otherwise we have to create a new one before adding people to list
    if fav is None:
        fav = Favorite(user_id=user_id)
        db.session.add(fav)
        db.session.commit()

    #If fav list exists, we check if already exists has the people we want to add
    stmt_people = select(FavPeople).where(
        FavPeople.fav_id == fav.id,
        FavPeople.people_id == people_id
        )
    fav_people = db.session.execute(stmt_people).scalar_one_or_none()

    #If found on the fav list, it returns an error
    if fav_people is not None:
        return jsonify({"error": "Person already added to list"}), 404
    
    #If not found on the fav list we add it
    new_fav_people = FavPeople(
        fav_id=fav.id,
        people_id=people_id
    )
    db.session.add(new_fav_people)
    db.session.commit()

    return jsonify(new_fav_people.serialize()), 201

# delete one user
@app.route("/users/<int:id>", methods=["DELETE"])
def delete_user(id):

    stmt = select(User).where(User.id == id)
    user = db.session.execute(stmt).scalar_one_or_none()

    if user is None:
        return jsonify({"error": "User not found"}), 404
    
    db.session.delete(user)
    db.session.commit()

    return jsonify({"message": "User deleted"}), 200

# delete one planet
@app.route("/planets/<int:id>", methods=["DELETE"])
def delete_planet(id):

    stmt = select(Planet).where(Planet.id == id)
    planet = db.session.execute(stmt).scalar_one_or_none()

    if planet is None:
        return jsonify({"error": "Planet not found"}), 404
    
    db.session.delete(planet)
    db.session.commit()

    return jsonify({"message": "Planet deleted"}), 200

# delete one people
@app.route("/peoples/<int:id>", methods=["DELETE"])
def delete_people(id):

    stmt = select(People).where(People.id == id)
    people = db.session.execute(stmt).scalar_one_or_none()

    if people is None:
        return jsonify({"error": "Person not found"}), 404
    
    db.session.delete(people)
    db.session.commit()

    return jsonify({"message": "Person deleted"}), 200

# delete one fav planet of user list
@app.route("/users/<int:user_id>/favorites/planets/<int:planet_id>", methods=["DELETE"])
def delete_fav_planet(user_id, planet_id):

    stmt = select(FavPlanet).where(
        FavPlanet.fav_id == user_id,
        FavPlanet.planet_id == planet_id
        )
    fav = db.session.execute(stmt).scalar_one_or_none()

    if fav is None:
        return jsonify({"error": "Planet not in list"}), 404
    
    db.session.delete(fav)
    db.session.commit()

    return jsonify({"message": "Planet deleted from list"}), 200

# delete one fav people of user list
@app.route("/users/<int:user_id>/favorites/peoples/<int:people_id>", methods=["DELETE"])
def delete_fav_people(user_id, people_id):

    #This time we se fav_id as now it is associated to the favorites.id after added with POST method
    stmt = select(FavPeople).where(
        FavPeople.fav_id == user_id,
        FavPeople.people_id == people_id
        )
    fav = db.session.execute(stmt).scalar_one_or_none()

    if fav is None:
        return jsonify({"error": "Person not in list"}), 404
    
    db.session.delete(fav)
    db.session.commit()

    return jsonify({"message": "Person deleted from list"}), 200

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
