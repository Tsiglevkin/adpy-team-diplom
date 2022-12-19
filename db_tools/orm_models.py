# Модуль в процессе доработки
#

from sqlalchemy import MetaData, Column, Integer, Boolean, String, ForeignKey
from sqlalchemy.orm import declarative_base
from bot_config.config import get_config

Base = declarative_base()
__DB_CONFIG__ = get_config('db', 'db.cfg')


def model_check(model_name, title):
    try:
        table_name = __DB_CONFIG__[title]
        return table_name
    except KeyError as ups:
        print(f'There were problems with table name of the {model_name} class: \n\t{ups} not correct!')
        print("\tВсё, кина не будет!")
        quit(1)
    except Exception as other:
        print(f'There were problems with table of the {model_name} class: \n\t{other}')
        print("\tВсё, кина не будет!")
        quit(1)


class VkinderUser(Base):  # Users
    __tablename__ = model_check('VkinderUser', 'VkinderUser table for bot fans')  # 'vkinder_users'

    id = Column(Integer, primary_key=True, index=True)

    def __str__(self):
        return f'VkinderUser id = {self.id}'


class MostMostUser(Base):
    __tablename__ = model_check('MostMostUser', 'Most-most users table')  # 'most_most_users'

    id = Column(Integer, primary_key=True, index=True)
    ban = Column(Boolean, nullable=False)

    def __str__(self):
        return f'MostMostUser id = {self.id}e'


class Bridge(Base):
    __tablename__ = model_check('Bridge', 'Table of relationships of db')  # 'bridge'

    user_id = Column(Integer, primary_key=True)
    ban_id = Column(Integer, primary_key=True)

    def __str__(self):  # не уверен в верности метода.
        return f'Bridge with user_id = {self.user_id} and ban_id = {self.ban_id}'


def create_tables(engine):
    Base.metadata.create_all(engine)
    var = Base.metadata.schema


def drop_tables(engine):
    Base.metadata.drop_all(engine)


def clear_table():
    pass
