from flask import Flask, request, make_response, jsonify
from flask_migrate import Migrate
from flask_restful import Api, Resource
from models import db, Hero, Power, HeroPower
import os

# Configuration
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

# Initialize extensions
migrate = Migrate(app, db)
db.init_app(app)
api = Api(app)

@app.route('/')
def index():
    return '<h1>Code Challenge</h1>'

# RESTful Resources
class Heroes(Resource):
    def get(self):
        heroes = [hero.to_dict(rules=('-hero_powers',)) for hero in Hero.query.all()]
        return make_response(jsonify(heroes), 200)
    
    def post(self):
        data = request.get_json()
        new_hero = Hero(
            name=data['name'],
            super_name=data['super_name']
        )
        db.session.add(new_hero)
        db.session.commit()
        return make_response(new_hero.to_dict(rules=('-hero_powers',)), 200)

class HeroesById(Resource):
    def get(self, id):
        hero = Hero.query.get(id)
        if hero:
            return make_response(hero.to_dict(), 200)
        return make_response(jsonify({'error': 'Hero not found'}), 404)

class Powers(Resource):
    def get(self):
        powers = [power.to_dict(rules=('-hero_powers', '-heroes')) for power in Power.query.all()]
        return make_response(jsonify(powers), 200)

class PowersById(Resource):
    def get(self, id):
        power = Power.query.get(id)
        if power:
            return make_response(power.to_dict(rules=('-hero_powers', '-heroes')), 200)
        return make_response(jsonify({'error': 'Power not found'}), 404)
    
    def patch(self, id):
        power = Power.query.get(id)
        if power:
            data = request.get_json()
            if 'description' in data:
                description = data['description']
                if not isinstance(description, str) or len(description) < 20:
                    return make_response(jsonify({'errors': ["validation errors"]}), 400)
                power.description = description
            db.session.commit()
            return make_response(power.to_dict(rules=('-hero_powers', '-heroes')), 200)
        return make_response(jsonify({'error': 'Power not found'}), 404)

class HeroPowers(Resource):
    def post(self):
        data = request.get_json()
        hero = Hero.query.get(data['hero_id'])
        power = Power.query.get(data['power_id'])
        if hero and power:
            strength = data.get('strength')
            if strength not in ['Strong', 'Weak', 'Average']:
                return make_response(jsonify({'errors': ["validation errors"]}), 400)
            new_hero_power = HeroPower(
                hero=hero,
                power=power,
                strength=strength
            )
            db.session.add(new_hero_power)
            db.session.commit()
            return make_response(new_hero_power.to_dict(), 200)
        return make_response(jsonify({'error': 'Hero or Power not found'}), 404)

# Registering Resources
api.add_resource(Heroes, '/heroes')
api.add_resource(HeroesById, '/heroes/<int:id>')
api.add_resource(Powers, '/powers')
api.add_resource(PowersById, '/powers/<int:id>')
api.add_resource(HeroPowers, '/hero_powers')

# Run the application
if __name__ == '__main__':
    app.run(port=5555, debug=True)
