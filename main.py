#

from vk_tools.vk_bot import VkBot

# import psycopg2
# import sqlalchemy
# from sqlalchemy.orm import sessionmaker
# from db_tools.models import create_tables, drop_tables, Users, Candidate, MarkList

# проверил через собственную БД - ошибок при запуске функций создания и удаления таблиц не было.

# user = 'postgres'
# password = 'введите свой пароль'
# host = 'localhost'
# base_name = 'vkinder_db'  # название можно сменить.
# DSN = f'postgresql://{user}:{password}@{host}:5432/{base_name}'
# engine = sqlalchemy.create_engine(DSN)

if __name__ == '__main__':
    bot = VkBot()
    bot.start()

    # create_tables(engine)
    # drop_tables(engine)

    # Session = sessionmaker(bind=engine)
    # session = Session()

    #
    #
    #
    # session.close()

