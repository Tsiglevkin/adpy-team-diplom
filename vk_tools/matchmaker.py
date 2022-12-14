#
from pprint import pprint
import vk_api

import sqlalchemy
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Session

from bot_config.config import get_config
from db_tools import orm_models as orm


def check_dict_keys(dict_, keys, msg='данных'):
    if not dict_ or not keys:
        return []
    for key in keys:
        try:
            dict_ = dict_[key]
        except KeyError as key_err:
            print(f'\nОшибка {msg}: отсутствует ключ {key_err}')
            return []
    return dict_


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

    def search_advisable_users(self, group_id='', client_id='', search_filter={},
                               vk_tools: vk_api.tools.VkTools = None) -> list:
        # db: Session = Depends(Matchmaker.get_db(self.SessionLocal))
        db = self.SessionLocal()
        for user in db.query(orm.Advisable).all():
            db.delete(user)
        Matchmaker.refresh_group_users(group_id, db, vk_tools)

        advisable_users = list(db.query(orm.Advisable).all())
        db.commit()
        db.close()
        return advisable_users

    def is_advisable_user_by_standard(self, group_id='', user_id='', search_filter={},
                                      vk_api_methods: vk_api.vk_api.VkApiMethod = None) -> bool:
        if not (group_id and user_id and search_filter):
            print('Недостаточно параметров! group, client, filter, vk_api_methods')
            return []
        # std_filter: dict = search_filter['standard']['services']
        std_fields = 'sex, city, bdate, counters'
        user = vk_api_methods.users.get(user_ids=user_id, fields=std_fields)[0]
        res = not user['is_closed']
        bot_filter: dict = self.get_standard_filter(search_filter)
        bot_fields = bot_filter['filter_bot_fields']
        for field_name in bot_fields:
            print(field_name)
            bot_field = bot_fields[field_name]
            vk_field = bot_field['filter_api_field'].strip().lower()
            if vk_field == 'sex':
                pass
            if vk_field == 'city':
                pass
            if vk_field == 'bdate':
                pass
            else:
                pass
        #
        print('Congratulations! The updated list of users of the group has been read and recorded in the database.')
        return res

    def get_standard_filter(self, search_filter={}) -> dict:
        if not search_filter:
            return {}
        try:
            std_filter: dict = search_filter['standard']['services']
            std = {}
            for field in ['button', 'filter_api_field']:
                std[field] = ', '.join(
                    std_filter[field_name][field] for field_name in std_filter if std_filter[field_name]['filter'])
            std['filter_bot_fields'] = dict((field_name, std_filter[field_name]) for field_name in std_filter
                                            if std_filter[field_name]['filter'])
            # pprint(std)
            return std
        except KeyError as key_err:
            print(f'\nОшибка данных: отсутствует ключ {key_err}\t( Matchmaker.get_standard_filter() )')
            return {}
        except Exception as other:
            print('Ошибка в Matchmaker.get_standard_filter():' + f'\n\t{other}')
            return {}

    @staticmethod
    def refresh_group_users(group_id='', db: Session = None, vk_tools: vk_api.tools.VkTools = None) -> list:
        if not (db and group_id and vk_tools):
            print('Недостаточно параметров! db, group, tools')
            return []
        print('\nRecording new users of VK group...')
        vk_users_added = []
        while True:
            vk_group_users_right_now = vk_tools.get_all('groups.getMembers', 1000, {'group_id': group_id})['items']
            pprint(vk_group_users_right_now)
            vk_users_added += list(vk_id for vk_id in vk_group_users_right_now if
                                   not db.query(orm.VkGroup).filter(orm.VkGroup.vk_id == vk_id).first())
            db.add_all(orm.VkGroup(vk_id=vk_id) for vk_id in vk_users_added)
            print('Added  to the VK group:', vk_users_added if vk_users_added else 'has no new users!')
            break
        db.commit()
        print('Congratulations! The updated list of users of the group has been read and recorded in the database.')
        return vk_users_added

    def print_advisable(self):
        db = self.SessionLocal()

        db.commit()
        db.close()
