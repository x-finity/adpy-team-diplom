import sqlalchemy as sq
from sqlalchemy.orm import declarative_base, relationship
import sys
import json


def load_config(filename):
    """Load config file from json"""
    with open(filename) as f:
        return json.load(f)


def dsn(config):
    """Create DSN from config"""
    db_config = config['database']
    db_config.setdefault('port', 5432)
    db_config.setdefault('host', 'localhost')
    db_config.setdefault('username', 'postgres')
    db_config.setdefault('drivername', 'postgresql')
    db_config.setdefault('password', '')
    return sq.URL.create(**db_config)


def create_db(engine):
    """Create database if not exists"""
    try:
        Base.metadata.create_all(engine)
    except sq.exc.OperationalError as e:
        sys.exit(f"Error: Cannot connect to database\n{e}")


config = load_config('config.json')
DSN = dsn(config)
Base = declarative_base()

class User(Base):
    __tablename__ = 'user'

    vk_user_id = sq.Column(sq.Integer, primary_key=True)
    name = sq.Column(sq.String(length=40), nullable=False)
    sex = sq.Column(sq.Boolean, unique=False)
    age = sq.Column(sq.Integer, nullable=False)
    city = sq.Column(sq.String(length=40), nullable=False)

    user_offer = relationship('UserOffer', back_populates='user')

    def __str__(self):
        return f'{self.vk_user_id, self.first_name, self.sex, self.age, self.city}'

class UserOffer(Base):
    __tablename__ = 'user_offer'

    user_offer_id = sq.Column(sq.Integer, primary_key=True)
    user_id1 = sq.Column(sq.Integer, sq.ForeignKey('user.vk_user_id'), nullable=False)
    user_id2 = sq.Column(sq.Integer, sq.ForeignKey('user.vk_user_id'), nullable=False)
    is_favorite = sq.Column(sq.Boolean, unique=False)
    is_blocked = sq.Column(sq.Boolean, unique=False)

    user = relationship('User', back_populates='user_offer')

    def __str__(self):
        return f'{self.user_offer_id, self.user_id1, self.user_id2, self.is_favorite, self.is_blocked}'


class Photo(Base):
    __tablename__ = 'photo'

    photo_id = sq.Column(sq.Integer, primary_key=True)
    user_id = sq.Column(sq.Integer, sq.ForeignKey('user.vk_user_id'), nullable=False)
    url = sq.Column(sq.String(length=200), unique=False)

    def __str__(self):
        return f'{self.photo_id, self.user_id, self.url}'

