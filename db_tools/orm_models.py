# Модуль в процессе доработки

from bot_config.config import get_config
import sqlalchemy as sq
from sqlalchemy.orm import declarative_base

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

    vk_id = sq.Column(sq.Integer, primary_key=True)

    def __str__(self):
        return f'VkGroup user with vk_id = {self.vk_id}'


class Advisable(Base):  # Candidate
    __tablename__ = model_check('Advisable', 'Advisables table for VK group user')   # 'user_advisable'

    vk_id = sq.Column(sq.Integer, primary_key=True)

    def __str__(self):
        return f'Advisables table for user with vk_id = {self.vk_id}'


class Chosen(Base):  # MarkList
    __tablename__ = model_check('Chosen', 'Table of interpersonal relationships')    # 'chosen'

    vk_id = sq.Column(sq.Integer, primary_key=True)
    chosen_vk_id = sq.Column(sq.Integer, primary_key=True)
    liked = sq.Column(sq.Boolean, nullable=False)

    def __str__(self):  # не уверен в верности метода.
        return f'Chosen vk_id = {self.chosen_id} for user vk_id = {self.vk_id}'


class ChosenUser(Base):  # MarkList
    __tablename__ = model_check('Chosen', 'Table of relationships of the chosen user')  # 'user_relationships'

    vk_id = sq.Column(sq.Integer, primary_key=True)
    chosen_vk_id = sq.Column(sq.Integer, primary_key=True)
    liked = sq.Column(sq.Boolean, nullable=False)

    def __str__(self):
        return f'Chosen user with vk_id = {self.chosen_id}'


def create_tables(engine):
    Base.metadata.create_all(engine)
    var = Base.metadata.schema


def drop_tables(engine):
    Base.metadata.drop_all(engine)


def clear_table():
    pass
