#
from pprint import pprint
import vk_api

import sqlalchemy
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Session
# from fastapi import Depends, FastAPI

from datetime import datetime, date

from vk_tools.vk_bot import VkBot
from vk_tools.standard_checker import StandardChecker, get_standard_filter
from bot_config.config import get_config
from db_tools import orm_models as orm


# app = FastAPI()


class Matchmaker(VkBot):

    def __init__(self, bot='bot.cfg', db='db.cfg'):
        super().__init__(bot)
        self._DB_CONFIG: dict = get_config('db', db)
        self.engine = sqlalchemy.create_engine(self.get_DSN())  # <class 'sqlalchemy.engine.base.Engine'>
        self.SessionLocal = sessionmaker(bind=self.engine)  # <class 'sqlalchemy.orm.session.sessionmaker'>
        self.checker = None
        if bool(self._DB_CONFIG['overwrite']):
            orm.drop_tables(self.engine)
        orm.create_tables(self.engine)
        print('A database {} with tables has been created, access is open.'.format(self._DB_CONFIG['dbase name']))

    def get_DSN(self) -> str:
        db = self._DB_CONFIG
        return 'postgresql://{}:{}@{}/{}'.format(db["login"], db["password"], db["server"], db["dbase name"])

    #
    # @staticmethod
    # def get_db(session_local):
    #     db = session_local()
    #     try:
    #         yield db
    #     finally:
    #         db.close()

    def refresh_group_users(self, db: Session = None) -> list:
        if not (db and self.group_id and self.vk_tools):
            print('Недостаточно параметров! db, group, tools')
            return []
        # db = self.SessionLocal()
        print('\nRecording new users of VK group...')
        vk_users_added = []
        while True:
            vk_group_users_right_now = self.vk_tools.get_all('groups.getMembers', 1000,
                                                             {'group_id': self.group_id})['items']
            pprint(vk_group_users_right_now)
            vk_users_added += list(vk_id for vk_id in vk_group_users_right_now if
                                   not db.query(orm.VkGroup).filter(orm.VkGroup.vk_id == vk_id).first())
            db.add_all(orm.VkGroup(vk_id=vk_id) for vk_id in vk_users_added)
            print('Added  to the VK group:', vk_users_added if vk_users_added else 'has no new users!')
            break
        db.commit()
        # db.close()
        print('Congratulations! The updated list of users of the group has been read and recorded in the database.')
        return vk_users_added

    def search_advisable_users(self, client_id='', search_filter={}, search_mode='No mass requests') -> list:
        # db: Session = Depends(Matchmaker.get_db(self.SessionLocal))
        db = self.SessionLocal()  # db: Session
        self.refresh_group_users(db)
        for user in db.query(orm.Advisable).all():
            db.delete(user)
        db.commit()
        print('Deleted records in Advisable')
        if search_mode != "No mass requests":
            pass
        # pprint(search_filter['standard'])   # -------------------
        #        ----------  Стандартный поиск  -----------
        bot_filter: dict = get_standard_filter(search_filter=search_filter)
        print('\n------ {}:\t'.format(search_filter['standard']['description'].strip().upper()), end='')
        if bot_filter['buttons']:
            print(bot_filter['buttons'])
            self.checker = StandardChecker(client_id=client_id, search_filter=search_filter,
                                           api_methods=self.vk_api_methods)
            db.add_all(orm.Advisable(vk_id=user.vk_id) for user in db.query(orm.VkGroup).all()
                       if self.checker.is_advisable_user(vk_id=user.vk_id))
        else:
            print('Стандартный фильтр не задан...')
            db.add_all(orm.Advisable(vk_id=user.vk_id) for user in db.query(orm.VkGroup).all())
        db.commit()
        advisable_users = list(user.vk_id for user in db.query(orm.Advisable).all())
        print(f'\n{advisable_users} --> was pulled into Advisable')
        db.close()
        return advisable_users

    def print_advisable(self):
        pass
