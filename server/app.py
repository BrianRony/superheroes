#!/usr/bin/env python3

from flask import Flask, request, jsonify
from flask_migrate import Migrate
from flask_restful import Api, Resource
from models import db, Hero, Power, HeroPower

import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)
api = Api(app)


class HeroListResource(Resource):
    def get(self):
        heroes = Hero.query.all()
        return jsonify([hero.to_dict(rules={'-hero_powers': True}) for hero in heroes])


class HeroDetailResource(Resource):
    def get(self, id):
        hero = db.session.get(Hero, id)  # Update here
        if hero is None:
            return {"error": "Hero not found"}, 404
        return jsonify(hero.to_dict())


class PowerListResource(Resource):
    def get(self):
        powers = Power.query.all()
        return jsonify([power.to_dict(rules={'-hero_powers': True}) for power in powers])



class PowerDetailResource(Resource):
    def get(self, id):
        power = db.session.get(Power, id)  # Update here
        if power is None:
            return {"error": "Power not found"}, 404
        return jsonify(power.to_dict(rules={'-hero_powers': True}))

    def patch(self, id):
        power = db.session.get(Power, id)  # Update here
        if power is None:
            return {"error": "Power not found"}, 404
        data = request.get_json()

        description = data.get('description')
        if description is not None:
            if len(description) < 20:
                return {"errors": ["validation errors"]}, 400
            power.description = description
            db.session.commit()
        
        return jsonify(power.to_dict())


class HeroPowerResource(Resource):
    def post(self):
        try:
            data = request.get_json()
            strength = data.get('strength')
            hero_id = data.get('hero_id')
            power_id = data.get('power_id')

            allowed_strengths = ['Weak', 'Average', 'Strong']
            if strength not in allowed_strengths:
                return {"errors": ["validation errors"]}, 400

            hero = db.session.get(Hero, hero_id)  # Update here
            power = db.session.get(Power, power_id)  # Update here
            if not hero or not power:
                return {"error": "Hero or Power not found"}, 404

            hero_power = HeroPower.query.filter_by(
                hero_id=hero_id, power_id=power_id).one_or_none()
            if hero_power:
                db.session.delete(hero_power)
                db.session.commit()

            hero_power = HeroPower(strength=strength, hero_id=hero_id, power_id=power_id)
            db.session.add(hero_power)
            db.session.commit()

            return jsonify({
                'id': hero_power.id,
                'strength': hero_power.strength,
                'hero_id': hero_power.hero_id,
                'power_id': hero_power.power_id,
                'hero': hero.to_dict(),
                'power': power.to_dict()
            })

        except Exception as e:
            # Log the exception for debugging
            print(f"Exception occurred: {e}")
            return {"error": "Internal Server Error"}, 500


# Add resources to API
api.add_resource(HeroListResource, '/heroes')
api.add_resource(HeroDetailResource, '/heroes/<int:id>')
api.add_resource(PowerListResource, '/powers')
api.add_resource(PowerDetailResource, '/powers/<int:id>')
api.add_resource(HeroPowerResource, '/hero_powers')

@app.route('/')
def index():
    return '<h1>Code challenge</h1>'


if __name__ == '__main__':
    app.run(port=5555, debug=True)
