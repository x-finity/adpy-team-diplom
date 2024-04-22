import sqlalchemy as sq
from sqlalchemy.orm import declarative_base, relationship


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


config = load_config('config.json')