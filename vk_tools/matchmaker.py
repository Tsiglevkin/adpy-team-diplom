#
from pprint import pprint
import vk_api

import sqlalchemy
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Session
# from fastapi import Depends, FastAPI

from bot_config.config import get_config
from db_tools import orm_models as orm


class Matchmaker:
    def __init__(self, db='db.cfg'):
        self._DB_CONFIG: dict = get_config('db', db)
        self.engine = sqlalchemy.create_engine(self.get_DSN())
        self.SessionLocal = sessionmaker(bind=self.engine)
        if bool(self._DB_CONFIG['overwrite']):
            orm.drop_tables(self.engine)
        orm.create_tables(self.engine)
        print('A database {} with tables has been created, access is open.'.format(self._DB_CONFIG['dbase name']))

    def get_DSN(self) -> str:
        db = self._DB_CONFIG
        return 'postgresql://{}:{}@{}/{}'.format(db["login"], db["password"], db["server"], db["dbase name"])

    def search_advisable_users(self, group_id: str = None,
                               vk_tools: vk_api.tools.VkTools = None,
                               search_filter_json_file: str = 'search_filter') -> list:
        db = self.SessionLocal()
        for user in db.query(orm.Advisable).all():
            db.delete(user)
        Matchmaker.refresh_group_users(db, group_id, vk_tools)

        db.commit()
        advisable_users = list(db.query(orm.Advisable).all())
        db.close()
        return advisable_users

    def get_filter_of_advisable_users(self):
        pass

    @staticmethod
    def refresh_group_users(db: Session = None, group_id: str = '', vk_tools: vk_api.tools.VkTools = None) -> list:
        if not (db and group_id and vk_tools):
            print('Недостаточно параметров! db, group, tools')
            return []
        print('Recording new users of VK group...')
        vk_users_added = []
        while True:
            vk_group_users_right_now = vk_tools.get_all('groups.getMembers', 1000, {'group_id': group_id})['items']
            pprint(vk_group_users_right_now)
            vk_users_added += list(vk_id for vk_id in vk_group_users_right_now if not db.query(orm.VkGroup).filter(orm.VkGroup.vk_id == vk_id).first())
            db.add_all(orm.VkGroup(vk_id=vk_id) for vk_id in vk_users_added)
            print('Added  to the VK group:', vk_users_added if vk_users_added else 'has no new users!')
            break
        db.commit()
        print('Congratulations! The updated list of users of the group has been read and recorded in the database.')
        return vk_users_added

    def print_advisable(self):
        db = self.SessionLocal()
