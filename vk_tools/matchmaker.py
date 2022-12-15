#
from pprint import pprint
import vk_api

import sqlalchemy
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Session

from bot_config.config import get_config
from db_tools import orm_models as orm


def in_deviation(dev, val, check_val) -> bool:
    val_dev = val + dev
    return val <= check_val <= val_dev if val_dev > val else val_dev <= check_val <= val


def field_value(any_dict, field_name=''):
    value = ''
    try:
        value = any_dict[field_name]
    except KeyError as key_err:
        print(f'\tОтсутствует поле значений: {key_err}')
    except Exception as other:
        print(other)
    return value


def user_info_(user: dict = {}) -> str:
    return "user{}: {} {} ({}) {} {}".format(
        user['id'], field_value(user, 'first_name'), field_value(user, 'last_name'),
        ['', 'жен', 'муж'][int(field_value(user, 'sex'))] if field_value(user, 'sex') else '',
        field_value(user, 'bdate'),
        field_value(user, 'city')['title'] if field_value(user, 'city') else '')


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

    #
    # @staticmethod
    # def get_db(session_local):
    #     db = session_local()
    #     try:
    #         yield db
    #     finally:
    #         db.close()

    def search_advisable_users(self, group_id='', client_id='', search_filter={},
                               vk_tools: vk_api.tools.VkTools = None,
                               vk_api_methods: vk_api.vk_api.VkApiMethod = None) -> list:
        client_fields = 'sex,city,bdate,counters'
        client_info = vk_api_methods.users.get(user_ids=client_id, fields=client_fields)[0]
        user_info_fields = 'sex, city, bdate, counters'
        # db: Session = Depends(Matchmaker.get_db(self.SessionLocal))
        db = self.SessionLocal()
        Matchmaker.refresh_group_users(group_id, db, vk_tools)
        for user in db.query(orm.Advisable).all():
            db.delete(user)
        db.commit()
        print('Deleted records in Advisable')
        #        ----------  Стандартный поиск  -----------
        bot_filter: dict = self.get_standard_filter(search_filter=search_filter)
        print('------ {}:\t'.format(search_filter['standard']['description'].strip().upper()), end='')
        if bot_filter['button']:
            print(bot_filter['button'])
            db.add_all(orm.Advisable(vk_id=user.vk_id) for user in db.query(orm.VkGroup).all()
                       if self.is_advisable_user_by_standard(
                user_info=vk_api_methods.users.get(user_ids=user.vk_id, fields=user_info_fields)[0],
                client_info=client_info, bot_filter=bot_filter))
        else:
            print('Стандартный фильтр не задан...')
            db.add_all(orm.Advisable(vk_id=user.vk_id) for user in db.query(orm.VkGroup).all())

        db.commit()
        advisable_users = list(user.vk_id for user in db.query(orm.Advisable).all())
        print(advisable_users, ' --> was pulled into Advisable')
        db.close()
        return advisable_users

    def is_advisable_user_by_standard(self, user_info={}, client_info={}, bot_filter={}) -> bool:
        if not (user_info and client_info and bot_filter):
            print('Недостаточно параметров! group, client, filter, vk_api_methods')
            return False
        res = not user_info['is_closed']
        if not res:
            return res
        bot_fields = bot_filter['filter_bot_fields']
        for field_name in bot_fields:
            bot_field = bot_fields[field_name]
            vk_user_field_name = bot_field['filter_api_field'].strip().lower()
            vk_val = field_value(user_info, vk_user_field_name)
            client_val = field_value(client_info, vk_user_field_name)
            bot_val = bot_field['filter_api_field_value']
            bot_dev = bot_field['filter_api_field_deviation_value']
            print('ПРОВЕРКА:', field_name, '=', bot_val)  # -------------------------------------
            if not bot_val:
                if client_val:
                    bot_val = client_val
                else:
                    res = not vk_val
                    break
            if not vk_val:
                res = False
                break
            # res = res and vk_val == bot_val or (bot_dev and bot_dev.isdigit() and int(bot_dev)
            #                                   and in_deviation(dev=int(bot_dev), val=bot_val, check_val=vk_val))
            if vk_user_field_name == 'sex':
                res = res and (str(vk_val) == str(bot_val))
            elif vk_user_field_name == 'city':
                vk_value = field_value(vk_val, 'title')
                filter_value = field_value(bot_val, 'title')
                print('{}, vk{}: {} -{}- filter: {}'.format(
                    res, user_info['id'], vk_value, vk_value == filter_value, filter_value))
                res = res and vk_value == filter_value
                print(res, vk_val, )
            elif vk_user_field_name == 'bdate':
                res = res and vk_val == bot_val
            else:
                pass
        print(f'Congratulations-2! Найден подходящий {user_info_(user_info)}'
              if res else f'\tПропускаем user{user_info["id"]}...')
        #
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
        # db = self.SessionLocal()
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
        # db.close()
        print('Congratulations! The updated list of users of the group has been read and recorded in the database.')
        return vk_users_added

    def print_advisable(self):
        pass
