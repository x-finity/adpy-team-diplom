import sqlalchemy as sq
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
import sys
import json
import vkapi
import os

def load_config(filename=None):
    """Load config file from json"""
    if filename:
        return json.load(open(filename))
    else:
        config = {key: value for key, value in dict(os.environ).items() if key.startswith('PG_')}
        config.update({'VK_GROUP_TOKEN': os.environ.get('VK_GROUP_TOKEN')})
        config.update({'VK_USER_TOKEN': os.environ.get('VK_USER_TOKEN')})
        return config


def dsn(config):
    """Create DSN from config"""
    db_config = {key[3:].lower(): value for key, value in config.items() if key.startswith('PG_')}
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


Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    vk_user_id = sq.Column(sq.Integer, primary_key=True)
    first_name = sq.Column(sq.String(length=40), nullable=False)
    last_name = sq.Column(sq.String(length=40), nullable=False)
    sex = sq.Column(sq.Boolean, unique=False)
    age = sq.Column(sq.Integer, nullable=False)
    city = sq.Column(sq.String(length=40), nullable=False)

    photo = relationship('Photo', back_populates='user', cascade="all,delete")

    def __str__(self):
        return f'{self.vk_user_id, self.first_name, self.sex, self.age, self.city}'


class UserOffer(Base):
    __tablename__ = 'user_offer'

    user_offer_id = sq.Column(sq.Integer, primary_key=True)
    person_id = sq.Column(sq.Integer, sq.ForeignKey('user.vk_user_id'), nullable=False)
    offer_id = sq.Column(sq.Integer, sq.ForeignKey('user.vk_user_id'), nullable=False)
    is_favorite = sq.Column(sq.Boolean, unique=False)
    is_blocked = sq.Column(sq.Boolean, unique=False)

    person = relationship('User', backref='person', foreign_keys=[person_id], cascade="all,delete")
    offer = relationship('User', backref='offer', foreign_keys=[offer_id], cascade="all,delete")

    def __str__(self):
        return f'{self.user_offer_id, self.user_id1, self.user_id2, self.is_favorite, self.is_blocked}'


class Photo(Base):
    __tablename__ = 'photo'

    photo_id = sq.Column(sq.Integer, primary_key=True)
    user_id = sq.Column(sq.Integer, sq.ForeignKey('user.vk_user_id'), nullable=False)
    url = sq.Column(sq.String(length=300), unique=False)

    user = relationship('User', back_populates='photo', cascade="all,delete")

    def __str__(self):
        return f'{self.photo_id, self.user_id, self.url}'


def push_user_to_db(session, token, user_id):
    user_info = vkapi.VkUserAPI(token).get_user_info(user_id)
    if user_info:
        if not session.query(User).filter(User.vk_user_id == user_id).first():
            session.add(User(vk_user_id=user_id, **user_info))
            for photo in vkapi.VkUserAPI(token).get_user_photos(user_id):
                session.add(Photo(user_id=user_id, url=photo))
            session.commit()


def del_user_from_db(session, user_id):
    session.query(Photo).filter(Photo.user_id == user_id).delete()
    if session.query(User).filter(User.vk_user_id == user_id).first():
        session.query(User).filter(User.vk_user_id == user_id).delete()
        session.commit()


def object_as_dict(obj):
    return {
        c.key: getattr(obj, c.key)
        for c in sq.inspect(obj).mapper.column_attrs
    }


def get_user_from_db(session, user_id):
    if session.query(User).filter(User.vk_user_id == user_id).first():
        user_info = object_as_dict(session.query(User).filter(User.vk_user_id == user_id).first())
        photos = session.query(Photo).filter(Photo.user_id == user_id).all()
        user_info['photos'] = [photo.url for photo in photos]
        return user_info


if __name__ == "__main__":
    config = load_config()
    # print(config)
    DSN = dsn(config)
    engine = sq.create_engine(DSN)
    create_db(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    push_user_to_db(session , config['VK_USER_TOKEN'], 1)
    push_user_to_db(session , config['VK_USER_TOKEN'], 126875243)
    del_user_from_db(session, 1)
    print(get_user_from_db(session, 86301318))
    print(get_user_from_db(session, 126875243))