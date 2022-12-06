#

from config import get_db_config
import sqlalchemy


class Matchmaker:
    def __init__(self, db: str = 'db.cfg'):
        self._DB_CONFIG = get_db_config(db)
        self.engine = sqlalchemy.create_engine(self.get_DSN())

    def get_DSN(self):
        return f'postgresql://{self._DB_CONFIG["login"]}:{self._DB_CONFIG["password"]}' \
               f'@{"localhost"}:5432/{self._DB_CONFIG["dbase_name"]}'

