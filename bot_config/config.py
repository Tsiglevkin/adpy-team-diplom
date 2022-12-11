#

import os
import json


def get_config(type_config='bot', config_file='bot.cfg', overwrite=True):
    config_dir = '/'
    file = config_dir + config_file
    response = {}
    if overwrite:
        print(f'The file {file} will be overwrite!')
    else:
        if config_file in os.listdir(config_dir):
            print(f'The file {file} already exists. Skipped...')
        else:
            print(f'The file {file} will be record!')
            overwrite = True
    if type_config == 'bot':
        response = read_json_file(config_file, write_json_file(get_bot_config_json(), file) if overwrite else None)
    elif type_config == 'db':
        response = read_json_file(config_file, write_json_file(get_db_config_json(), file) if overwrite else None)
    elif type_config == 'bot_menu':
        response = read_json_file(config_file, write_json_file(get_bot_menu_config_json(), file) if overwrite else None)
    return response


def read_json_file(file, dict_: dict = None):
    if dict_:
        return dict_
    try:
        with open(file, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError as ex:
        print(f'File "{file}" not found...\n\t{ex}\n')
    except OSError as other:
        print(f'При открытии файла "{file}" возникли проблемы: \n\t{other}\n')
    print('Не получилось создать бот: недостаточно информации! ')
    quit(1)


def write_json_file(dict_, file):
    try:
        with open(file, 'w', encoding='utf-8') as f:
            json.dump(dict_, f, ensure_ascii=False, indent=2)
        print(f'Congratulations! The config was saved to {file}')
    except OSError as other:
        print(f'There were problems opening the file {file}: \n\t{other}')
        print('Sorry, the results are not saved to a json file...')
        quit(1)
    return dict_


def get_db_config_json():
    return {
        'login': 'postgres',
        'password': '4sql%pg',
        'dbase name': 'vkinder',
        'server': 'localhost:5432',
        'scheme': 'public',
        "overwrite": '',
        'VK group table': 'vk_group',
        'Advisables table for VK group user': 'user_advisable',
        'Table of relationships of the chosen user': 'user_relationships',
        'Table of interpersonal relationships': 'chosen'
    }


def get_bot_config_json():
    return {
        'name': 'VKinder10',
        'group_id': '217491346',
        'token': 'vk1.a.-Y1qvpVh8DSjq4SHejdoJXPf089sA5Kuqnc40NVHx1uEUxEhe0r4d9vtlaD2gX9ABtm'
                 'JlxECTemdmVRc5ZGNCe92pN76NdNjXAc4631s5-xzreQi2Ojv59BGidAJvy6VUgLEo5IlZUHGK'
                 '-1JGJir0dHY2k4bPHlky2nk0fks8miDKMrQdO2lvyhqakGVsiz1RCBF3i7hXxx_AGXWdXINew',
        'greetings': 'привет, hi, чао, вечер в хату',
        'farewells': 'пока, by, адьюс, не скучай, быть добру'
    }


def get_bot_menu_config_json():
    return {
        'mode': {
            'start-up': {
                'button': 'Вежливый',
                'command': '@@',
                'service_code': '1',
                'description': '',
                'max_buttons_peer_line': '',
                'services': {
                    'matchmaker': {
                        'button': 'НЯША',
                        'command': '@@/!',
                        'service_code': '11',
                        'description': 'мои любимчики',
                        'max_buttons_peer_line': '',
                        'services': {
                            'search': {
                                'button': 'НАЙТИ',
                                'command': '@@/?',
                                'service_code': '111',
                                'description': 'поиск интересных пиплов',
                                'max_buttons_peer_line': '',
                                'services': {
                                    'filter': {
                                        'button': 'Фильтр',
                                        'command': '@@/f',
                                        'service_code': '1231',
                                        'description': 'Фильтры поиска',
                                        'max_buttons_peer_line': '2',
                                        'services': {
                                            'standard': {
                                                'button': 'Стандартный',
                                                'command': '@@/>',
                                                'service_code': '12311',
                                                'description': 'Стандартный поиск',
                                                'max_buttons_peer_line': '',
                                                'services': {
                                                    'male': {
                                                        'command': '@@/gender:m',
                                                        'button': 'Муж',
                                                        'service_code': '123411',
                                                        'description': 'Мужчина',
                                                        'max_buttons_peer_line': '',
                                                        'services': {}},
                                                    'female': {
                                                        'command': '@@/gender:f',
                                                        'button': 'Жен',
                                                        'service_code': '123412',
                                                        'description': 'Женщина',
                                                        'max_buttons_peer_line': '',
                                                        'services': {}},
                                                    'any gender': {
                                                        'command': '@@/gender:?',
                                                        'button': 'любой пол',
                                                        'service_code': '123413',
                                                        'description': '',
                                                        'max_buttons_peer_line': '',
                                                        'services': {}},
                                                    'younger': {
                                                        'command': '@@/age:-',
                                                        'button': 'моложе',
                                                        'service_code': '123414',
                                                        'description': 'Моложе-0',
                                                        'max_buttons_peer_line': '',
                                                        'services': {}},
                                                    'older': {
                                                        'command': '@@/age:+',
                                                        'button': 'старше',
                                                        'service_code': '123415',
                                                        'description': 'Старше+0',
                                                        'max_buttons_peer_line': '',
                                                        'services': {}},
                                                    'any age': {
                                                        'command': '@@/age:?',
                                                        'button': 'любой возраст',
                                                        'service_code': '123416',
                                                        'description': '',
                                                        'max_buttons_peer_line': '',
                                                        'services': {}},
                                                    'city': {
                                                        'command': '@@/city:!',
                                                        'button': 'Город',
                                                        'service_code': '123417',
                                                        'description': 'Твой город',
                                                        'max_buttons_peer_line': '',
                                                        'services': {}},
                                                    'any city': {
                                                        'command': '@@/city:?',
                                                        'button': 'любой город',
                                                        'service_code': '123418',
                                                        'description': 'город не имеет значения',
                                                        'max_buttons_peer_line': '',
                                                        'services': {}},
                                                    'exit': {
                                                        'command': '@@/',
                                                        'button': 'Сохранить',
                                                        'service_code': '12319',
                                                        'description': 'Выход из режима настройки фильтров',
                                                        'max_buttons_peer_line': '',
                                                        'services': {}}
                                                }},
                                            'interests': {
                                                'command': '@@/+',
                                                'button': 'По интересам',
                                                'service_code': '12312',
                                                'description': 'Поиск по интересам',
                                                'max_buttons_peer_line': '',
                                                'services': {}},
                                            'advanced': {
                                                'command': '@@/+',
                                                'button': 'Продвинутый',
                                                'service_code': '12313',
                                                'description': 'Продвинутый поиск',
                                                'max_buttons_peer_line': '',
                                                'services': {}},
                                            'exit': {
                                                'command': '@@/',
                                                'button': 'Применить фильтр',
                                                'service_code': '12314',
                                                'description': 'Выход из режима фильтров поиска',
                                                'max_buttons_peer_line': '',
                                                'services': {}}
                                        }},
                                    'advisable': {
                                        'command': '@@/?',
                                        'button': 'ПОИСК',
                                        'service_code': '1232',
                                        'description': 'Рекомендуем',
                                        'max_buttons_peer_line': '',
                                        'services': {
                                            'next': {
                                                'command': '@@/>',
                                                'button': 'Следующий',
                                                'service_code': '12321',
                                                'description': '',
                                                'max_buttons_peer_line': '',
                                                'services': {}},
                                            'save': {
                                                'command': '@@/+',
                                                'button': 'Сохранить',
                                                'service_code': '12322',
                                                'description': '',
                                                'max_buttons_peer_line': '',
                                                'services': {}},
                                            'exit': {
                                                'command': '@@/',
                                                'button': 'Выход',
                                                'service_code': '12323',
                                                'description': 'Выход из режима просмотра результатов поиска',
                                                'max_buttons_peer_line': '',
                                                'services': {}}
                                        }},
                                    'exit': {
                                        'command': '@@/',
                                        'button': 'Выход',
                                        'service_code': '1233',
                                        'description': 'Выход из режима поиска подходящих пользователей',
                                        'max_buttons_peer_line': '',
                                        'services': {}}
                                }},
                            'print': {
                                'command': '@@/!',
                                'button': 'Список',
                                'service_code': '112',
                                'description': 'СПИСОК моих пиплов',
                                'max_buttons_peer_line': '',
                                'services': {}},
                            'exit': {
                                'command': '@@/',
                                'button': 'Выход',
                                'service_code': '113',
                                'description': '',
                                'max_buttons_peer_line': '',
                                'services': {}}}}}}}
    }
