# Проверяем пользователей на соответствие СТАНДАРТНОМУ фильтру

from datetime import datetime, date
from vk_api.vk_api import VkApi, VkApiMethod
from vk_tools.checker import VkUserChecker


def get_standard_filter(search_filter={}) -> dict:
    if not search_filter:
        return {}
    try:
        std_filter: dict = search_filter['standard']['services']
        std = {}
        for field in ['button', 'filter_api_field']:
            std[field + 's'] = ', '.join(
                std_filter[field_name][field] for field_name in std_filter if std_filter[field_name]['filter'])
        std['filter_bot_fields'] = dict((field_name, std_filter[field_name]) for field_name in std_filter
                                        if std_filter[field_name]['filter'])
        return std
    except KeyError as key_err:
        print(f'\nОшибка данных: отсутствует ключ {key_err}\t( Matchmaker.get_standard_filter() )')
        return {}
    except Exception as other:
        print('\nОшибка в Matchmaker.get_standard_filter():' + f'\n\t{other}')
        return {}


def in_int_deviation(val_dev: int, val: int, check_val: int) -> bool:
    dev = val + val_dev
    return val < check_val <= val_dev + dev or val + dev <= check_val < val


def correct_date(date_string: str) -> datetime:
    null_date = datetime.strptime('1.1.1000', "%d.%m.%Y")
    if not date_string.strip():
        return null_date
    try:
        bdate = datetime.strptime(date_string, "%d.%m.%Y")
    except ValueError:
        print('\tНекорректная дата или отсутствует!', date_string)
        date_list = date_string.split('.', 3)
        l = len(date_list)
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


class StandardChecker(VkUserChecker):
    _skill = 'A matchmaker standard Search Engine'

    def __init__(self, client_id: str, api_methods: VkApiMethod, search_filter: dict = {}):
        super(StandardChecker, self).__init__(client_id, api_methods, search_filter, self._skill)

    def is_advisable_user_by_standard(self, vk_id: str) -> bool:
        super(StandardChecker, self).is_advisable_user_by_standard(vk_id)
        bot_filter: dict = get_standard_filter(self.search_filter)
        if not self.get_control_attr(bot_filter):
            return False
        person_filter = dict([api_field, False] for api_field in bot_filter.get('filter_api_fields', '').split(', '))
        bot_fields = bot_filter['filter_bot_fields']
        res = True
        for bot_field_name, bot_field in bot_fields.items():
            vk_field_name = bot_field.get('filter_api_field', '')
            if person_filter[vk_field_name]:
                continue
            vk_val = self.user_info.get(vk_field_name, '')
            client_val = self.client_info.get(vk_field_name, '')
            filter_val = bot_field.get('filter_api_field_value', '')
            filter_dev = bot_field.get('filter_api_field_deviation_value', '0')
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
            check_result = self._check_print_person_filter(field_name=vk_field_name, vk_val=vk_val,
                                                           filter_val=filter_val, filter_deviation=filter_dev)
            person_filter[vk_field_name] = person_filter[vk_field_name] or check_result
            if person_filter[vk_field_name]:
                print(f'\tПРОШЁЛ по фильтру {vk_field_name.upper()} бродяга user{vk_id}!')
        return self.check_print_filters(filters=person_filter, res=res, vk_id=vk_id)

    def check_print_filters(self, filters, res, vk_id):
        for field_name, field_filter in filters.items():
            print('\t Фильтр', field_name, '=', field_filter)  # ------------------------------
            res = res and field_filter
            if not res:
                print(f'\tНЕ ПРОШЁЛ по фильтру {field_name.upper()} бродяга user{vk_id}!')
                break
        print(f'\nCongratulations! Найден подходящий {self}\n'
              if res else f'\tПропускаем user{vk_id}...')
        return res

    def get_control_attr(self, bot_filter):
        if not (self.user_info and self.client_info and bot_filter):
            print('Недостаточно параметров! user, client, filter')
            return False
        if self.user_id == self.client_id:
            print(f'\nСамого клиента user{self.user_id} не рассматриваем, пропускаем!\n')
            return False
        if self.user_info['is_closed']:
            print(f'\nАккаунт user{self.user_id} ЗАКРЫТ!\n')
            return False
        return True

    def _check_print_person_filter(self, field_name, vk_val, filter_val, filter_deviation) -> bool:
        check_result = False
        if field_name == 'sex':
            check_result = int(vk_val) == int(filter_val)
            print(f'\tvk{self.user_id}: {vk_val} -{check_result}- filter: {filter_val}')
        elif field_name == 'city':
            vk_value = vk_val.get('title', '')
            filter_value = filter_val.get('title', '')
            check_result = vk_value == filter_value
            print(f'\tvk{self.user_id}: {vk_value} -{check_result}- filter: {filter_value}')
        elif field_name == 'bdate':
            vk_value = correct_date(vk_val).year
            filter_value = correct_date(filter_val).year
            filter_dev = int(filter_deviation) if filter_deviation and str(filter_deviation).isdigit() else 0
            if filter_dev:
                check_result = in_int_deviation(val_dev=filter_dev, val=filter_value, check_val=vk_value)
                print(f'\tvk{self.user_id}: {vk_value} -{check_result}- filter: {filter_value}'
                      f' с интервалом ({filter_dev})')
            else:
                check_result = vk_val == filter_val
                print(f'\tvk{self.user_id}: {vk_value} -{check_result}- filter: {filter_value}')
        else:
            print('Ошибка: проверялись не те поля!')  # -------------------------------
        return check_result
