#

from config import get_db_config
from vk_tools.vk_bot import VkBot
import sqlalchemy


class Matchmaker(VkBot):
    def __init__(self, bot: str = 'bot.cfg', db: str = 'db.cfg'):
        super(Matchmaker, self).__init__(bot)
        self._DB_CONFIG = get_db_config(db)
        self.engine = sqlalchemy.create_engine(self.get_DSN())

    def get_DSN(self):
        return f'postgresql://{self._DB_CONFIG["login"]}:{self._DB_CONFIG["password"]}' \
               f'@{"localhost"}:5432/{self._DB_CONFIG["dbase_name"]}'
