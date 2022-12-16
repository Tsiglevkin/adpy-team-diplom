#
from pprint import pprint
import vk_api

import sqlalchemy
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Session

from datetime import datetime, date

from bot_config.config import get_config
from db_tools import orm_models as orm


def is_advisable_user_by_standard(user_info={}, client_info={}, bot_filter={}) -> bool:
    if not (user_info and client_info and bot_filter):
        print('Недостаточно параметров! group, client, filter, vk_api_methods')
        return False
    res = not user_info['is_closed']
    if not res:
        return res
    person_filter = dict([api_field, False] for api_field in bot_filter['filter_api_field'].split(', '))
    bot_fields = bot_filter['filter_bot_fields']
    # pprint(bot_fields)  # ----------------------------------
    for bot_field_name, bot_field in bot_fields.items():
        vk_field_name = bot_field['filter_api_field']
        if person_filter[vk_field_name]:
            continue
        vk_val = user_info.get(vk_field_name, '')
        client_val = client_info.get(vk_field_name, '')
        filter_val = bot_field['filter_api_field_value']
        filter_dev = bot_field['filter_api_field_deviation_value']
        print('ПРОВЕРКА:', bot_field_name, '=', filter_val)  # -------------------------------------
        if not filter_val:
            if client_val:
                filter_val = client_val
            else:
                res = not vk_val
                break
        if not vk_val:
            res = False
            break
        check_result = check_print_person_filter(field_name=vk_field_name, user_info=user_info, vk_val=vk_val,
                                                 filter_val=filter_val, filter_deviation=filter_dev)
        person_filter[vk_field_name] = person_filter[vk_field_name] or check_result
        if person_filter[vk_field_name]:
            print(f'\tПРОШЁЛ по фильтру {vk_field_name.upper()} бродяга user{user_info["id"]}!')
    for field_name, field_filter in person_filter.items():
        print('\t Фильтр', field_name, '=', field_filter)  # ------------------------------
        res = res and field_filter
        if not res:
            print(f'\tНЕ ПРОШЁЛ по фильтру {field_name.upper()} бродяга user{user_info["id"]}!')
            break
    print(f'\nCongratulations! Найден подходящий {user_info_(user_info)}\n'
          if res else f'\tПропускаем user{user_info["id"]}...')  #
    return res


def check_print_person_filter(field_name, user_info, vk_val, filter_val, filter_deviation) -> bool:
    check_result = False
    if field_name == 'sex':
        check_result = int(vk_val) == int(filter_val)
        print(f'\tvk{user_info["id"]}: {vk_val} -{check_result}- filter: {filter_val}')
    elif field_name == 'city':
        vk_value = vk_val.get('title', '')
        filter_value = filter_val.get('title', '')
        check_result = vk_value == filter_value
        print(f'\tvk{user_info["id"]}: {vk_value} -{check_result}- filter: {filter_value}')
    elif field_name == 'bdate':
        vk_value = correct_date(vk_val).year
        filter_value = correct_date(filter_val).year
        filter_dev = int(filter_deviation) if filter_deviation and str(filter_deviation).isdigit() else 0
        if filter_dev:
            check_result = in_deviation(val_dev=filter_dev, val=filter_value, check_val=vk_value)
            print(f'\tvk{user_info["id"]}: {vk_value} -{check_result}- filter: {filter_value}'
                  f' с интервалом ({filter_dev})')
        else:
            check_result = vk_val == filter_val
            print(f'\tvk{user_info["id"]}: {vk_value} -{check_result}- filter: {filter_value}')
    else:
        print('Ошибка: проверялись не те поля!')  # -------------------------------
    return check_result


def get_standard_filter(search_filter={}) -> dict:
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
        print('\nОшибка в Matchmaker.get_standard_filter():' + f'\n\t{other}')
        return {}


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


def in_deviation(val_dev, val, check_val) -> bool:
    dev = val + val_dev
    return val <= check_val <= val_dev + dev or val + dev <= check_val <= val


def correct_date(date_string: str = '') -> datetime:
    null_date = datetime.strptime('1.1.1000', "%d.%m.%Y")
    if not date_string.strip():
        return null_date
    try:
        bdate = datetime.strptime(date_string, "%d.%m.%Y")
    except ValueError:
        print('\tНекорректная дата или отсутствует!', date_string)
        date_list = date_string.split('.', 3)
        l = len(date_list)
        # print(date_list)
        if l == 0:
            return null_date
        if l > 0:
            if not date_list[0].isdigit():
                date_list[0] = '1'
            elif not (0 < int(date_list[0]) < 32):
                date_list[0] = '1'
        if l > 1:
            if not date_list[1].isdigit():
                date_list[1] = '1'
            elif not (0 < int(date_list[1]) < 13):
                date_list[1] = '1'
        else:
            date_list.append('1000')
        if l > 2:
            if date_list[2].isdigit():
                if not (1000 < int(date_list[2]) <= date.today().year):
                    date_list[2] = '1000'
            else:
                date_list[2] = '1000'
        else:
            date_list.append('1000')
        return datetime.strptime('.'.join(date_list), "%d.%m.%Y")
    except Exception as other:
        print('\tОшибка обработки даты!', other)
        return null_date
    return bdate


def user_info_(user: dict = {}) -> str:
    return "user{}: {} {} ({}) {} {}".format(
        user['id'], user.get('first_name', ''), user.get('last_name', ''),
        ['', 'жен', 'муж'][int(user.get('sex', ''))] if user.get('sex', '') else '',
        user.get('bdate', ''),
        user.get('city', '')['title'] if user.get('city', '') else '')


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
                               vk_tools: vk_api.tools.VkTools = None,
                               vk_api_methods: vk_api.vk_api.VkApiMethod = None) -> list:
        client_fields = 'sex,city,bdate,counters'
        client_info = vk_api_methods.users.get(user_ids=client_id, fields=client_fields)[0]
        user_info_fields = 'sex, city, bdate, counters'
        # db: Session = Depends(Matchmaker.get_db(self.SessionLocal))
        db = self.SessionLocal()
        refresh_group_users(db, vk_tools)
        for user in db.query(orm.Advisable).all():
            db.delete(user)
        db.commit()
        print('Deleted records in Advisable')
        #        ----------  Стандартный поиск  -----------
        bot_filter: dict = get_standard_filter(search_filter=search_filter)
        print('------ {}:\t'.format(search_filter['standard']['description'].strip().upper()), end='')
        if bot_filter['button']:
            print(bot_filter['button'])
            db.add_all(orm.Advisable(vk_id=user.vk_id) for user in db.query(orm.VkGroup).all()
                       if is_advisable_user_by_standard(
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

    def print_advisable(self):
        pass
