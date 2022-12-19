# Модуль в процессе доработки

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


class VkGroup(Base):  # Users
    __tablename__ = model_check('VKGroup', 'VK group table')  # 'vk_group'

    id = Column(Integer, primary_key=True)

    def __str__(self):
        return f'VkGroup user with id = {self.id}'


class Advisable(Base):  # Candidate
    __tablename__ = model_check('Advisable', 'Advisables table for VK group user')   # 'user_advisable'

    id = Column(Integer, primary_key=True)
    liked = Column(Boolean, nullable=False)

    def __str__(self):
        return f'user with id = {self.id} from Advisable table'


class Chosen(Base):  # MarkList
    __tablename__ = model_check('Chosen', 'Table of interpersonal relationships')    # 'chosen'

    id = Column(Integer, primary_key=True)
    chosen_vk_id = Column(Integer, primary_key=True)
    liked = Column(Boolean, nullable=False)

    def __str__(self):  # не уверен в верности метода.
        return f'Chosen id = {self.id} for user vk_id = {self.id}'


class ChosenUser(Base):  # MarkList
    __tablename__ = model_check('Chosen', 'Table of relationships of the chosen user')  # 'user_relationships'

    id = Column(Integer, primary_key=True)
    chosen_vk_id = Column(Integer, primary_key=True)
    liked = Column(Boolean, nullable=False)

    def __str__(self):
        return f'Chosen user with id = {self.id}'


def create_tables(engine):
    Base.metadata.create_all(engine)
    var = Base.metadata.schema


def drop_tables(engine):
    Base.metadata.drop_all(engine)


def clear_table():
    pass
