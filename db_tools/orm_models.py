#

from sqlalchemy import MetaData, Column, Integer, Boolean, Date, String, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
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


class VKinder(Base):  # Users
    __tablename__ = model_check('Vkinder', 'Vkinder table for VKbot fans')  # 'vkinders'

    vk_id = Column(Integer, primary_key=True, index=True)
    first_visit_date = Column(Date, nullable=False)

    def __str__(self):
        return f'Vkinder user id = {self.id}'


class VkIdol(Base):
    __tablename__ = model_check('VKIdol', 'VKIdol users table')  # 'vk_idols'

    id = Column(Integer, primary_key=True, autoincrement=True)
    vk_idol_id = Column(Integer, unique=True, nullable=False, index=True)
    vk_id = Column(Integer, ForeignKey('vkinders.vk_id'), primary_key=True)
    ban = Column(Boolean, nullable=False)
    rec_date = Column(Date, nullable=False)
    idols = relationship(VKinder, backref='vkinders')

    def __str__(self):
        return f'MostMostUser id = {self.id}e'


def create_tables(engine):
    Base.metadata.create_all(engine)
    var = Base.metadata.schema


def drop_tables(engine):
    Base.metadata.drop_all(engine)


def clear_table():
    pass
