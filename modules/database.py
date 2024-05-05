import sqlalchemy as sq
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
import sys
import json
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


def create_dsn(config):
    """Create DSN from config"""
    db_config = {key[3:].lower(): value for key, value in config.items() if key.startswith('PG_')}
    db_config.setdefault('port', 5432)
    db_config.setdefault('host', 'localhost')
    db_config.setdefault('username', 'postgres')
    db_config.setdefault('drivername', 'postgresql')
    db_config.setdefault('password', 'postgres')
    return sq.URL.create(**db_config)


def create_db(engine):
    """Create database if not exists"""
    try:
        Base.metadata.create_all(engine)
    except sq.exc.OperationalError as e:
        sys.exit(f"Error: Cannot connect to database\n{e}")


def create_session(config):
    dsn = create_dsn(config)
    engine = sq.create_engine(dsn)
    create_db(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    return session


def object_as_dict(obj):
    return {
        c.key: getattr(obj, c.key)
        for c in sq.inspect(obj).mapper.column_attrs
    }


Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    vk_user_id = sq.Column(sq.Integer, primary_key=True)
    first_name = sq.Column(sq.String(length=40), nullable=False)
    last_name = sq.Column(sq.String(length=40), nullable=False)
    sex = sq.Column(sq.SmallInteger, unique=False)
    age = sq.Column(sq.SmallInteger, nullable=False)
    city = sq.Column(sq.String(length=40), nullable=False)
    offset = sq.Column(sq.SmallInteger, unique=False)

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


class AppDB:
    def __init__(self, config):
        self.config = config
        self.session = create_session(config)

    def add_user_to_db(self, user_id, photo_list, **kwargs):
        if not self.session.query(User).filter(User.vk_user_id == user_id).first():
            self.session.add(User(vk_user_id=user_id, offset=0, **kwargs))
            for photo in photo_list:
                self.session.add(Photo(user_id=user_id, url=photo))
            self.session.commit()

    def del_user_from_db(self, user_id):
        self.session.query(Photo).filter(Photo.user_id == user_id).delete()
        self.session.query(UserOffer).filter(UserOffer.person_id == user_id).delete()
        self.session.query(UserOffer).filter(UserOffer.offer_id == user_id).delete()
        self.session.query(User).filter(User.vk_user_id == user_id).delete()
        self.session.commit()

    def add_matching_to_db(self, user_id1, user_id2, is_favorite=False, is_blocked=False):
        if not self.session.query(UserOffer).filter(UserOffer.person_id == user_id1, UserOffer.offer_id == user_id2).first():
            self.session.add(UserOffer(person_id=user_id1, offer_id=user_id2, is_favorite=is_favorite, is_blocked=is_blocked))
            self.session.commit()

    def del_matching_from_db(self, user_id1, user_id2):
        self.session.query(UserOffer).filter(UserOffer.person_id == user_id1, UserOffer.offer_id == user_id2).delete()
        self.session.commit()

    def get_user_from_db(self, user_id):
        if self.session.query(User).filter(User.vk_user_id == user_id).first():
            user_info = object_as_dict(self.session.query(User).filter(User.vk_user_id == user_id).first())
            photos = self.session.query(Photo).filter(Photo.user_id == user_id).all()
            user_info['photos'] = [photo.url for photo in photos]
            return user_info
        return None

    def list_users_from_db(self):
        return [user.vk_user_id for user in self.session.query(User).all()]

    def modify_matching_to_blacklist(self, person_id, offer_id, is_blocked=True):
        if self.session.query(UserOffer).filter(UserOffer.person_id == person_id, UserOffer.offer_id == offer_id).first():
            (self.session.query(UserOffer).filter(UserOffer.person_id == person_id, UserOffer.offer_id == offer_id).
             update({"is_blocked": is_blocked}))
            self.session.commit()

    def modify_matching_to_favorite(self, person_id, offer_id, is_favorite=True):
        if self.session.query(UserOffer).filter(UserOffer.person_id == person_id, UserOffer.offer_id == offer_id).first():
            (self.session.query(UserOffer).filter(UserOffer.person_id == person_id, UserOffer.offer_id == offer_id).
             update({"is_favorite": is_favorite}))
            self.session.commit()

    def modify_offset(self, user_id, amount):
        old_offset = self.session.query(User).filter(User.vk_user_id == user_id).first().offset
        if self.session.query(User).filter(User.vk_user_id == user_id).first():
            (self.session.query(User).filter(User.vk_user_id == user_id).update({"offset": old_offset + amount}))
            self.session.commit()

    def is_blocked(self, person_id, offer_id):
        query = self.session.query(UserOffer).filter(UserOffer.person_id == person_id, UserOffer.offer_id == offer_id).first()
        if query:
            return query.is_blocked
    

if __name__ == "__main__":
    pass
