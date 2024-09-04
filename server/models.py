from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})

db = SQLAlchemy(metadata=metadata)

class Hero(db.Model, SerializerMixin):
    __tablename__ = 'heroes'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    super_name = db.Column(db.String, nullable=False)

    # relationships
    hero_powers = db.relationship('HeroPower', back_populates='hero', cascade="all, delete-orphan")
    powers = association_proxy('hero_powers', 'power')

    # serialization rules
    serialize_rules = ('-hero_powers.hero', '-powers.hero_powers')

    def __repr__(self):
        return f'<Hero {self.id}: {self.name} aka {self.super_name}>'


class Power(db.Model, SerializerMixin):
    __tablename__ = 'powers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)

    # relationships
    hero_powers = db.relationship('HeroPower', back_populates='power', cascade="all, delete-orphan")
    heroes = association_proxy('hero_powers', 'hero')

    # serialization rules
    serialize_rules = ('-hero_powers.power', '-heroes.hero_powers')

    # validation
    @validates('description')
    def validate_description(self, key, value):
        if len(value) < 20:
            raise ValueError("Description must be at least 20 characters long.")
        return value

    def __repr__(self):
        return f'<Power {self.id}: {self.name}>'


class HeroPower(db.Model, SerializerMixin):
    __tablename__ = 'hero_powers'

    id = db.Column(db.Integer, primary_key=True)
    strength = db.Column(db.String, nullable=False)

    # relationships
    hero_id = db.Column(db.Integer, db.ForeignKey('heroes.id'), nullable=False)
    power_id = db.Column(db.Integer, db.ForeignKey('powers.id'), nullable=False)

    hero = db.relationship('Hero', back_populates='hero_powers')
    power = db.relationship('Power', back_populates='hero_powers')

    # serialization rules
    serialize_rules = ('-hero.hero_powers', '-power.hero_powers')

    # validation
    @validates('strength')
    def validate_strength(self, key, value):
        allowed_strengths = ['Strong', 'Weak', 'Average']
        if value not in allowed_strengths:
            raise ValueError(f"Strength must be one of: {', '.join(allowed_strengths)}")
        return value

    def __repr__(self):
        return f'<HeroPower {self.id}: {self.strength}>'
