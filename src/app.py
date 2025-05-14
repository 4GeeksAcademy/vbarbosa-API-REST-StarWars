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
from models import db, User, Profile, Planet, People
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

# GET all users
@app.route('/admin/user', methods=['GET'])
def get_users():
    statement = select(User)
    # el scalars() se ocupa de devolverlos como objeto, sino seran devueltos como tuplas.
    # como tupla NO pueden ejecutar el serialize
    users = db.session.execute(statement).scalars().all()
    return jsonify([user.serialize() for user in users]), 200

# GET only one user
@app.route('/admin/user/<int:user_id>', methods=['GET'])
def get_user(user_id):
    statement = select(User).where(User.id == user_id)
    user = db.session.execute(statement).scalar_one_or_none()
    if user is None:
        return jsonify({"error": "User not found"}), 404

    return jsonify(user.serialize()), 200

# GET all profiles
@app.route('/admin/profile', methods=['GET'])
def get_profiles():
    statement = select(Profile)
    profiles = db.session.execute(statement).scalars().all()
    return jsonify([profile.serialize() for profile in profiles]), 200

# GET only one profile
@app.route('/admin/profile/<int:profile_id>', methods=['GET'])
def get_profile(profile_id):
    statement = select(Profile).where(Profile.id == profile_id)
    profile = db.session.execute(statement).scalar_one_or_none()
    if profile is None:
        return jsonify({"error": "No profile created"}), 404

    return jsonify(profile.serialize()), 200

# GET all planets
@app.route('/admin/planets', methods=['GET'])
def get_planets():
    statement = select(Planet)
    planets = db.session.execute(statement).scalars().all()
    return jsonify([planet.serialize() for planet in planets]), 200

# GET only one planet
@app.route('/admin/planets/<int:planet_id>', methods=['GET'])
def get_planet(planet_id):
    statement = select(Planet).where(Planet.id == planet_id)
    planet = db.session.execute(statement).scalar_one_or_none()
    if planet is None:
        return jsonify({"error": "Planet not found"}), 404

    return jsonify(planet.serialize()), 200

# GET all people
@app.route('/admin/peoples', methods=['GET'])
def get_all_peoples():
    statement = select(People)
    peoples = db.session.execute(statement).scalars().all()
    return jsonify([people.serialize() for people in peoples]), 200

# GET only one people
@app.route('/admin/peoples/<int:people_id>', methods=['GET'])
def get_person(people_id):
    statement = select(People).where(People.id == people_id)
    people = db.session.execute(statement).scalar_one_or_none()
    if people is None:
        return jsonify({"error": "Person not found"}), 404

    return jsonify(people.serialize()), 200

# GET all favourites planets
@app.route('/admin/profile/<int:profile_id>/planets', methods=['GET'])
def get_profile_planets(profile_id):
    statement = select(Profile).where(Profile.id == profile_id)
    profile = db.session.execute(statement).scalar_one_or_none()

    if profile is None:
        return jsonify({"error": "No profile created"}), 404
    
    planets = profile.planets
    return jsonify([planet.serialize() for planet in planets]), 200

# GET all favourites people
@app.route('/admin/profile/<int:profile_id>/peoples', methods=['GET'])
def get_user_people(profile_id):
    statement = select(Profile).where(Profile.id == profile_id)
    profile = db.session.execute(statement).scalar_one_or_none()

    if profile is None:
        return jsonify({"error": "No profile created"}), 404
    
    peoples = profile.peoples
    return jsonify([people.serialize() for people in peoples]), 200

# Create user account
@app.route("/admin/user", methods=["POST"])
def create_user():
    data = request.get_json()
    if not data or "email" not in data or "password" not in data:
        return jsonify({"error": "Missing data"}), 400
    new_user = User(
        email=data["email"],
        password=data["password"],
    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify(new_user.serialize()), 201

# Create a profile
@app.route("/admin/profile", methods=["POST"])
def create_profile():
    data = request.get_json()
    if not data or "name" not in data or "user_id" not in data:
        return jsonify({"error": "Missing data"}), 400
    new_profile = Profile(name=data["name"], user_id=data["user_id"], last_name=data["last_name"])
    db.session.add(new_profile)
    db.session.commit()
    return jsonify(new_profile.serialize()), 201

# Add planet to favourite list
@app.route("/admin/profile/<int:profile_id>/planets", methods=["POST"])
def create_planet(profile_id):
    data = request.get_json()
    if "name" not in data:
        return jsonify({"error": "Name is required"}), 400
    new_planet = Planet(name=data["name"])
    db.session.add(new_planet)
    db.session.commit()
    return jsonify(new_planet.serialize()), 201

# Add people to favourite list
@app.route("/admin/profile/<int:profile_id>/peoples", methods=["POST"])
def create_people(profile_id):
    data = request.get_json()
    if "name" not in data or "profile_id" not in data:
        return jsonify({"error": "No element on list"}), 400
    new_person = People(name=data["name"], profile_id=data["profile_id"])
    db.session.add(new_person)
    db.session.commit()
    return jsonify(new_person.serialize()), 201

# delete one user
@app.route("/admin/user/<int:id>", methods=["DELETE"])
def delete_user(id):
    stmt = select(User).where(User.id == id)
    user = db.session.execute(stmt).scalar_one_or_none()
    if user is None:
        return jsonify({"error": "User not found"}), 404
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "User deleted"}), 200

# delete user profile, we cannot have more than one
@app.route("/admin/profile/<int:id>", methods=["DELETE"])
def delete_profile(id):
    stmt = select(Profile).where(Profile.id == id)
    profile = db.session.execute(stmt).scalar_one_or_none()
    if profile is None:
        return jsonify({"error": "No profile created"}), 404
    db.session.delete(profile)
    db.session.commit()
    return jsonify({"message": "Profile deleted, add new profile"}), 200

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
