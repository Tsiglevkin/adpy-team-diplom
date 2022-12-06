#

from vk_tools.vk_bot import VkBot

import psycopg2
import sqlalchemy
from sqlalchemy.orm import sessionmaker
from db_tools.models import create_tables, drop_tables, Users, Candidate, MarkList
from db_tools.models import show_black_list, show_all_candidates_id, show_all_like_candidates, add_id_to_users, \
    add_id_to_candidates, add_id_to_marklist, get_like, get_dislike, delete_mark

# проверил через собственную БД - ошибок при запуске функций создания и удаления таблиц не было.

user = 'postgres'
password = 'введите свой пароль'
host = 'localhost'
base_name = 'vkinder_db'  # название можно сменить.
DSN = f'postgresql://{user}:{password}@{host}:5432/{base_name}'
engine = sqlalchemy.create_engine(DSN)

if __name__ == '__main__':
    bot = VkBot()
    bot.start()

    # a little change

    # create_tables(engine)
    # drop_tables(engine)

    # Session = sessionmaker(bind=engine)
    # session = Session()

    # пробы функций
    # add_id_to_users(some_session=session, user_vk_id_list=[123, 465, 789, 987, 654, 321])
    # add_id_to_candidates(some_session=session, candidate_vk_id_list=[123, 456, 798, 357, 159])
    # add_id_to_marklist(some_session=session, user_vk_id=123, candidate_vk_id=456)
    # add_id_to_marklist(some_session=session, user_vk_id=123, candidate_vk_id=357)
    # add_id_to_marklist(some_session=session, user_vk_id=465, candidate_vk_id=456)
    # add_id_to_marklist(some_session=session, user_vk_id=123, candidate_vk_id=798)
    # add_id_to_marklist(some_session=session, user_vk_id=465, candidate_vk_id=159)
    # get_like(some_session=session, user_vk_id=123, candidate_vk_id=456)
    # get_like(some_session=session, user_vk_id=465, candidate_vk_id=456)
    # get_dislike(some_session=session, user_vk_id=123, candidate_vk_id=798)
    # get_dislike(some_session=session, user_vk_id=465, candidate_vk_id=159)
    #
    # print(show_all_candidates_id(some_session=session, user_vk_id=123))
    # print(show_all_like_candidates(some_session=session, user_vk_id=123))
    # print(show_black_list(some_session=session, user_vk_id=465))
    # print(delete_mark(some_session=session, user_vk_id=465, candidate_vk_id=159))
    # # все функции работают.
    # session.close()

